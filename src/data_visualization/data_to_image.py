# * Library imports
import asyncio
import cv2
import numpy as np
from typing import List, Tuple, Optional

# * File imports
from ..data_buffer import get_raw_buffered_data, get_processed_buffered_temp_data, polygon_data_buffer
from ..data_handling import divide_into_quadrants, get_quadrant_statistics


class DataToImage:
    def __init__(self):
        self.show_quadrants = False
        self.show_stats = True
        self.polygon_points: List[Tuple[int, int]] = []
        self.polygon_mode = False
        self.min_points = 4
        self.max_points = 10
        self.current_matrix = None
        self.current_processed_data = None  # Store processed temperature data
        self.heatmap_scale = (640, 512)  # Display size
        self.point_radius = 10  # Click detection radius

    def find_nearest_point(self, x, y) -> Optional[int]:
        """Find the nearest point within click radius"""
        min_dist = float('inf')
        nearest_idx = None

        for i, point in enumerate(self.polygon_points):
            dist = np.sqrt((point[0] - x) ** 2 + (point[1] - y) ** 2)
            if dist < min_dist and dist <= self.point_radius:
                min_dist = dist
                nearest_idx = i

        return nearest_idx

    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse clicks for polygon point selection and removal"""
        if self.polygon_mode:
            # Left click - Add point
            if event == cv2.EVENT_LBUTTONDOWN:
                if len(self.polygon_points) < self.max_points:
                    self.polygon_points.append((x, y))
                    print(f"Point {len(self.polygon_points)} added: ({x}, {y})")
                else:
                    print(f"Maximum {self.max_points} points reached!")

            # Right click - Remove nearest point
            elif event == cv2.EVENT_RBUTTONDOWN:
                nearest_idx = self.find_nearest_point(x, y)
                if nearest_idx is not None:
                    removed_point = self.polygon_points.pop(nearest_idx)
                    print(f"Point {nearest_idx + 1} removed: {removed_point}")
                    print(f"Remaining points: {len(self.polygon_points)}")
                else:
                    print("No point nearby to remove")

    def draw_polygon(self, overlay):
        """Draw the polygon and points on the overlay"""
        if len(self.polygon_points) > 0:
            # Draw points with larger hover detection area
            for i, point in enumerate(self.polygon_points):
                # Draw hover area (semi-transparent)
                temp_overlay = overlay.copy()
                cv2.circle(temp_overlay, point, self.point_radius, (100, 100, 100), 1)
                cv2.addWeighted(temp_overlay, 0.3, overlay, 0.7, 0, overlay)

                # Draw actual point
                cv2.circle(overlay, point, 5, (0, 255, 0), -1)
                cv2.putText(overlay, str(i + 1), (point[0] + 10, point[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Draw lines connecting points
            if len(self.polygon_points) > 1:
                pts = np.array(self.polygon_points, np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(overlay, [pts], isClosed=True, color=(0, 255, 0), thickness=2)

    def get_data_points_in_polygon(self, processed_data: np.ndarray) -> np.ndarray:
        """
        Extract processed temperature data point values that fall within the polygon region
        Returns: array of temperature values
        """
        if len(self.polygon_points) < self.min_points:
            return np.array([])

        rows, cols = processed_data.shape

        # Scale polygon points from display size to matrix size
        scale_x = cols / self.heatmap_scale[0]
        scale_y = rows / self.heatmap_scale[1]

        scaled_points = [(int(x * scale_x), int(y * scale_y))
                         for x, y in self.polygon_points]

        # Create mask for the polygon region
        mask = np.zeros((rows, cols), dtype=np.uint8)
        pts = np.array(scaled_points, np.int32)
        cv2.fillPoly(mask, [pts], 1)

        # Get processed temperature values of points inside polygon
        temp_values = processed_data[mask == 1]

        return temp_values

    def print_polygon_data(self, processed_data: np.ndarray):
        """Print processed temperature data point values within polygon to console"""
        values = self.get_data_points_in_polygon(processed_data)

        if len(values) == 0:
            print("No data points in polygon region")
            return

        print(f"\n{len(values)} data points:")
        print(values)
        print()

    def export_polygon_data(self, processed_data: np.ndarray, filename: str = "polygon_data.txt"):
        """Export processed temperature data point values within polygon to a file"""
        values = self.get_data_points_in_polygon(processed_data)

        if len(values) == 0:
            print("No data points in polygon region")
            return

        # Save to file - just the values
        np.savetxt(filename, values, fmt='%.4f')

        print(f"\n{len(values)} data points exported to {filename}\n")

    def draw_quadrant_lines(self, overlay, mid_row=255, mid_col=320):
        height, width = overlay.shape[:2]

        cv2.line(overlay, (0, mid_row), (width, mid_row), (255, 255, 255), 2)
        cv2.line(overlay, (mid_col, 0), (mid_col, height), (255, 255, 255), 2)

        font = cv2.FONT_ITALIC
        font_scale = 0.6
        color = (255, 255, 255)
        thickness = 2

        cv2.putText(overlay, "Q1", (10, 25), font, font_scale, color, thickness)
        cv2.putText(overlay, "Q2", (mid_col + 10, 25), font, font_scale, color, thickness)
        cv2.putText(overlay, "Q3", (10, mid_row + 25), font, font_scale, color, thickness)
        cv2.putText(overlay, "Q4", (mid_col + 10, mid_row + 25), font, font_scale, color, thickness)

    async def data_to_image(self) -> None:
        try:
            cv2.namedWindow("Thermal Image")
            cv2.setMouseCallback("Thermal Image", self.mouse_callback)

            while True:
                processed_buffer = get_processed_buffered_temp_data()

                if not processed_buffer:
                    print("Warning: No buffered data available.")
                    await asyncio.sleep(1)
                    continue

                matrix = processed_buffer[-1]

                # Store processed temperature data
                self.current_processed_data = matrix
                self.current_matrix = matrix

                # ALWAYS update polygon buffer if polygon is valid
                if len(self.polygon_points) >= self.min_points:
                    values = self.get_data_points_in_polygon(self.current_processed_data)
                    if len(values) > 0:
                        polygon_data_buffer.add(values)

                matrix_norm = cv2.normalize(matrix, None, 0, 255, cv2.NORM_MINMAX)

                if matrix_norm is None or matrix_norm.size == 0:
                    print("Warning: Normalized matrix is empty.")
                    await asyncio.sleep(1)
                    continue

                matrix_norm = np.uint8(matrix_norm)
                heatmap = cv2.applyColorMap(matrix_norm, cv2.COLORMAP_JET)

                # Resize for display
                heatmap = cv2.resize(heatmap, self.heatmap_scale)
                overlay = heatmap.copy()

                # Draw quadrants if enabled
                if self.show_quadrants:
                    quadrants = divide_into_quadrants(matrix)
                    q1, q2, q3, q4, mid_row, mid_col = quadrants
                    get_quadrant_statistics(q1, q2, q3, q4)

                    # Scale quadrant lines to display size
                    scale_x = self.heatmap_scale[0] / matrix.shape[1]
                    scale_y = self.heatmap_scale[1] / matrix.shape[0]
                    display_mid_row = int(mid_row * scale_y)
                    display_mid_col = int(mid_col * scale_x)

                    self.draw_quadrant_lines(overlay, display_mid_row, display_mid_col)

                # Draw polygon if points exist
                if len(self.polygon_points) > 0:
                    self.draw_polygon(overlay)

                # Show mode indicator
                if self.polygon_mode:
                    mode_text = f"POLYGON MODE - Points: {len(self.polygon_points)}/{self.max_points}"
                    cv2.putText(overlay, mode_text, (10, overlay.shape[0] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    # Show instructions
                    instructions = "L-Click: Add | R-Click: Remove"
                    cv2.putText(overlay, instructions, (10, overlay.shape[0] - 35),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                cv2.imshow("Thermal Image", overlay)

                key = cv2.waitKey(1) & 0xFF

                if key == 27:  # ESC
                    break
                elif key == ord('p'):  # Toggle polygon mode
                    self.polygon_mode = not self.polygon_mode
                    print(f"Polygon mode: {'ON' if self.polygon_mode else 'OFF'}")
                elif key == ord('c'):  # Clear all points
                    self.polygon_points.clear()
                    print("All polygon points cleared")
                elif key == ord('u'):  # Undo last point
                    if len(self.polygon_points) > 0:
                        removed = self.polygon_points.pop()
                        print(f"Last point removed: {removed}")
                    else:
                        print("No points to undo")
                elif key == ord('q'):  # Toggle quadrants
                    self.show_quadrants = not self.show_quadrants
                    print(f"Quadrants: {'ON' if self.show_quadrants else 'OFF'}")

                await asyncio.sleep(0)

        except Exception as e:
            print(f"Error in data_to_image: {e}")

        finally:
            cv2.destroyAllWindows()
            print("Thermal analysis stopped.")
# * Library imports
import asyncio
import cv2
import numpy as np
from typing import List, Tuple, Optional
from pathlib import Path
from datetime import datetime
import struct


# * File imports
# Mock the buffer functions for testing
def get_processed_buffered_temp_data():
    """Mock function that reads from data.txt instead of buffer"""
    try:
        data = np.loadtxt("data/test_data/data.txt")
        return [data]  # Return as list to mimic buffer behavior
    except Exception as e:
        print(f"Error loading data.txt: {e}")
        return []


# Mock polygon data buffer for testing
class MockPolygonDataBuffer:
    def __init__(self, max_size: int = 10):
        from collections import deque
        self.buffer = deque(maxlen=max_size)

    def add(self, data: np.ndarray):
        self.buffer.append(data)

    def export(self) -> list:
        return list(self.buffer)


polygon_data_buffer = MockPolygonDataBuffer()


class DataToImageTest:
    def __init__(self):
        self.show_quadrants = False
        self.show_stats = True
        self.polygon_points: List[Tuple[int, int]] = []
        self.polygon_mode = False
        self.min_points = 4
        self.max_points = 10
        self.current_matrix = None
        self.current_processed_data = None
        self.heatmap_scale = (640, 512)
        self.point_radius = 10
        self.output_dir = Path("./test_exports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Recording state
        self.is_recording = False
        self.recording_file = None
        self.recording_handle = None
        self.frame_count = 0
        self.recording_task = None

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
            if event == cv2.EVENT_LBUTTONDOWN:
                if len(self.polygon_points) < self.max_points:
                    self.polygon_points.append((x, y))
                    print(f"Point {len(self.polygon_points)} added: ({x}, {y})")
                else:
                    print(f"Maximum {self.max_points} points reached!")

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
            for i, point in enumerate(self.polygon_points):
                temp_overlay = overlay.copy()
                cv2.circle(temp_overlay, point, self.point_radius, (100, 100, 100), 1)
                cv2.addWeighted(temp_overlay, 0.3, overlay, 0.7, 0, overlay)

                cv2.circle(overlay, point, 5, (0, 255, 0), -1)
                cv2.putText(overlay, str(i + 1), (point[0] + 10, point[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            if len(self.polygon_points) > 1:
                pts = np.array(self.polygon_points, np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(overlay, [pts], isClosed=True, color=(0, 255, 0), thickness=2)

    def get_polygon_matrix(self, processed_data: np.ndarray) -> np.ndarray:
        """Extract polygon region as a proper 2D matrix with masked values"""
        # If no polygon defined, return entire matrix
        if len(self.polygon_points) < self.min_points:
            return processed_data

        rows, cols = processed_data.shape

        scale_x = cols / self.heatmap_scale[0]
        scale_y = rows / self.heatmap_scale[1]

        scaled_points = [(int(x * scale_x), int(y * scale_y))
                         for x, y in self.polygon_points]

        mask = np.zeros((rows, cols), dtype=np.uint8)
        pts = np.array(scaled_points, np.int32)
        cv2.fillPoly(mask, [pts], 1)

        output_matrix = np.where(mask == 1, processed_data, np.nan)

        return output_matrix

    def start_recording(self):
        """Start recording polygon data"""
        if self.is_recording:
            print("Already recording!")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.recording_file = self.output_dir / f"thermal_recording_{timestamp}.bin"
        self.recording_handle = open(self.recording_file, 'wb')
        self.is_recording = True
        self.frame_count = 0

        # Write file header with magic number for validation
        self.recording_handle.write(b'THRM')  # Magic number
        self.recording_handle.write(struct.pack('i', 1))  # Version number

        if len(self.polygon_points) < self.min_points:
            print(f"Started recording FULL FRAME to: {self.recording_file}")
        else:
            print(f"Started recording POLYGON REGION to: {self.recording_file}")

    def stop_recording(self):
        """Stop recording polygon data"""
        if not self.is_recording:
            print("Not recording!")
            return

        self.is_recording = False
        if self.recording_handle:
            self.recording_handle.close()
            self.recording_handle = None

        print(f"Recording stopped. {self.frame_count} frames saved to: {self.recording_file}")

    def write_frame(self, matrix_data):
        """Write a single frame to the recording file"""
        if not self.is_recording or not self.recording_handle:
            return

        try:
            # Frame divider: magic bytes
            self.recording_handle.write(b'FRAM')  # Frame marker

            # Write frame metadata
            self.recording_handle.write(struct.pack('i', len(matrix_data.shape)))  # num dimensions
            for dim in matrix_data.shape:
                self.recording_handle.write(struct.pack('i', dim))  # shape

            # Write timestamp
            timestamp_val = datetime.now().timestamp()
            self.recording_handle.write(struct.pack('d', timestamp_val))

            # Write frame number
            self.recording_handle.write(struct.pack('i', self.frame_count))

            # Write data as binary
            matrix_data.astype(np.float64).tofile(self.recording_handle)
            self.recording_handle.flush()

            self.frame_count += 1
            print(f"Frame {self.frame_count} written")

        except Exception as e:
            print(f"Error writing frame: {e}")

    async def recording_loop(self):
        """Background task that records frames every 1 second"""
        while self.is_recording:
            if self.current_processed_data is not None:
                matrix_to_record = self.get_polygon_matrix(self.current_processed_data)
                if matrix_to_record.size > 0:
                    self.write_frame(matrix_to_record)

            await asyncio.sleep(1.0)  # Record every 1 second

    async def data_to_image(self) -> None:
        try:
            cv2.namedWindow("Thermal Image Test")
            cv2.setMouseCallback("Thermal Image Test", self.mouse_callback)

            print("\nTest Mode - Reading from data.txt")
            print("\nControls:")
            print("  'p' - Toggle polygon mode")
            print("  LEFT CLICK - Add point (in polygon mode)")
            print("  RIGHT CLICK - Remove nearest point (in polygon mode)")
            print("  'c' - Clear all points")
            print("  'u' - Undo last point")
            print("  'r' - Start/Stop recording (1 second intervals)")
            print("  'b' - Print buffer contents")
            print("  ESC - Exit\n")
            print("Note: Recording without polygon will capture FULL FRAME\n")

            while True:
                processed_buffer = get_processed_buffered_temp_data()

                if not processed_buffer:
                    print("Warning: No data available from data.txt")
                    await asyncio.sleep(1)
                    continue

                matrix = processed_buffer[-1]

                self.current_processed_data = matrix
                self.current_matrix = matrix

                # Update polygon buffer
                matrix_to_buffer = self.get_polygon_matrix(self.current_processed_data)
                if matrix_to_buffer.size > 0:
                    polygon_data_buffer.add(matrix_to_buffer)

                matrix_norm = cv2.normalize(matrix, None, 0, 255, cv2.NORM_MINMAX)

                if matrix_norm is None or matrix_norm.size == 0:
                    print("Warning: Normalized matrix is empty.")
                    await asyncio.sleep(1)
                    continue

                matrix_norm = np.uint8(matrix_norm)
                heatmap = cv2.applyColorMap(matrix_norm, cv2.COLORMAP_JET)

                heatmap = cv2.resize(heatmap, self.heatmap_scale)
                overlay = heatmap.copy()

                # Draw polygon if points exist
                if len(self.polygon_points) > 0:
                    self.draw_polygon(overlay)

                # Show mode indicator
                if self.polygon_mode:
                    mode_text = f"POLYGON MODE - Points: {len(self.polygon_points)}/{self.max_points}"
                    cv2.putText(overlay, mode_text, (10, overlay.shape[0] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    instructions = "L-Click: Add | R-Click: Remove"
                    cv2.putText(overlay, instructions, (10, overlay.shape[0] - 35),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                # Show recording indicator
                if self.is_recording:
                    if len(self.polygon_points) < self.min_points:
                        rec_text = f"REC FULL - Frame {self.frame_count}"
                    else:
                        rec_text = f"REC POLYGON - Frame {self.frame_count}"
                    cv2.circle(overlay, (overlay.shape[1] - 30, 30), 10, (0, 0, 255), -1)
                    cv2.putText(overlay, rec_text, (overlay.shape[1] - 280, 35),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                cv2.imshow("Thermal Image Test", overlay)

                key = cv2.waitKey(1) & 0xFF

                if key == 27:
                    if self.is_recording:
                        self.stop_recording()
                    break
                elif key == ord('p'):
                    self.polygon_mode = not self.polygon_mode
                    print(f"Polygon mode: {'ON' if self.polygon_mode else 'OFF'}")
                elif key == ord('c'):
                    self.polygon_points.clear()
                    print("All polygon points cleared")
                elif key == ord('u'):
                    if len(self.polygon_points) > 0:
                        removed = self.polygon_points.pop()
                        print(f"Last point removed: {removed}")
                    else:
                        print("No points to undo")
                elif key == ord('r'):
                    if not self.is_recording:
                        self.start_recording()
                        self.recording_task = asyncio.create_task(self.recording_loop())
                    else:
                        self.stop_recording()
                        if self.recording_task:
                            self.recording_task.cancel()

                await asyncio.sleep(0.05)

        except Exception as e:
            print(f"Error in data_to_image: {e}")
            import traceback
            traceback.print_exc()

        finally:
            if self.is_recording:
                self.stop_recording()
            cv2.destroyAllWindows()
            print("Test stopped.")

if __name__ == "__main__":
    test = DataToImageTest()
    asyncio.run(test.data_to_image())
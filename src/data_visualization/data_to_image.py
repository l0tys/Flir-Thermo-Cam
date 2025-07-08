# * Library imports
import asyncio
import cv2
import numpy as np

# * File imports
from data_buffer import get_raw_buffered_data, get_processed_buffered_temp_data
from data_handling import divide_into_quadrants, get_quadrant_statistics


class DataToImage:
    def __init__(self):
        self.show_quadrants = True
        self.show_stats = True

    def draw_quadrant_lines(self, overlay, mid_row=255 , mid_col=320):
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
            while True:
                processed_buffer = get_raw_buffered_data()

                if not processed_buffer:
                    print("Warning: No buffered data available.")
                    await asyncio.sleep(1)
                    continue

                data = processed_buffer[-1]
                # data = np.loadtxt("data/test_data/data.txt")

                # matrix = 0.0107143 * data - 44.2857
                matrix = 0.0130303 * data - 62.4242
                matrix_norm = cv2.normalize(matrix, None, 0, 255, cv2.NORM_MINMAX)

                if matrix_norm is None or matrix_norm.size == 0:
                    print("Warning: Normalized matrix is empty.")
                    await asyncio.sleep(1)
                    continue

                matrix_norm = np.uint8(matrix_norm)
                heatmap = cv2.applyColorMap(matrix_norm, cv2.COLORMAP_JET)

                overlay = heatmap.copy()

                quadrants = divide_into_quadrants(matrix)
                q1, q2, q3, q4, mid_row, mid_col = quadrants

                get_quadrant_statistics(q1, q2, q3, q4)

                if self.show_quadrants:
                    self.draw_quadrant_lines(overlay, mid_row, mid_col)

                cv2.imshow("Thermal Image", overlay)

                if cv2.waitKey(1) == 27:
                    break

                await asyncio.sleep(0)

        except Exception as e:
            print(f"Error in data_to_image: {e}")

        finally:
            cv2.destroyAllWindows()
            print("Thermal analysis stopped.")
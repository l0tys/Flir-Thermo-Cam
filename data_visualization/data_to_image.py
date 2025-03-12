# * Library imports
import asyncio
import cv2
import numpy as np

# * File imports
from data_buffer import get_raw_buffered_data, processed_data_buffer

class DataToImage:
    def __init__(self, data_buffer=processed_data_buffer):
        self.data_buffer = data_buffer
        self.current_position: tuple = (0, 0)
        self.point_list = []

    def temp_hover(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            self.current_position = (x, y)

    async def data_to_image(self, processed_buffer=processed_data_buffer) -> None:
        cv2.namedWindow("Camera Image")
        cv2.setMouseCallback("Camera Image", self.temp_hover)

        try:
            while True:
                raw_buffer = get_raw_buffered_data()

                if not raw_buffer:
                    print("Warning: No buffered data available.")
                    await asyncio.sleep(1)
                    continue

                data = raw_buffer[-1]

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

                x, y = self.current_position
                if 0 <= y < matrix.shape[0] and 0 <= x < matrix.shape[1]:
                    temp = matrix[y, x]
                    self.point_list.append(temp)
                    processed_buffer.add(temp)
                    cv2.putText(overlay, f"Temp: {temp:.2f} C", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

                cv2.imshow("Camera Image", overlay)

                if cv2.waitKey(1) == 27:
                    break

                await asyncio.sleep(0)

        except Exception as e:
            print(f"Error in data_to_image: {e}")

        finally:
            cv2.destroyAllWindows()
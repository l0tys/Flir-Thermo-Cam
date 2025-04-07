# * Library imports
import asyncio
import cv2
import numpy as np

# * File imports
from data_buffer import get_processed_buffered_temp_data
from .color_map import create_thermal_colormap


class DataToImage:
    def __init__(self, data_buffer=None):
        self.data_buffer = data_buffer or get_processed_buffered_temp_data()
        self.current_position: tuple = (0, 0)

        self.thermal_lut = create_thermal_colormap()

    def temp_hover(self, event, x, y, flags, param):
        if event == cv2.EVENT_MOUSEMOVE:
            self.current_position = (x, y)

    async def data_to_image(self) -> None:
        cv2.namedWindow("Camera Image")
        cv2.setMouseCallback("Camera Image", self.temp_hover)

        try:
            while True:
                self.data_buffer = get_processed_buffered_temp_data()

                if not self.data_buffer:
                    print("Warning: No buffered data available.")
                    await asyncio.sleep(1)
                    continue

                data_buffer = np.array(self.data_buffer)

                matrix_norm = cv2.normalize(data_buffer, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

                if matrix_norm.size == 0:
                    print("Warning: Normalized matrix is empty.")
                    await asyncio.sleep(1)
                    continue

                try:
                    color_input = cv2.cvtColor(matrix_norm, cv2.COLOR_GRAY2BGR)
                    heatmap = cv2.LUT(color_input, self.thermal_lut)
                except Exception as e:
                    print(f"LUT failed, using fallback: {str(e)}")
                    heatmap = cv2.applyColorMap(matrix_norm, cv2.COLORMAP_JET)

                overlay = heatmap.copy()

                x, y = self.current_position
                if (0 <= y < data_buffer.shape[0] and
                        0 <= x < data_buffer.shape[1]):
                    temp = data_buffer[y, x]

                    cv2.putText(
                        overlay, f"Temp: {temp:.2f}C", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (255, 255, 255), 2, cv2.LINE_AA
                    )

                cv2.imshow("Camera Image", overlay)

                if cv2.waitKey(1) == 27:
                    break

                await asyncio.sleep(0)

        except Exception as e:
            print(f"Error in data_to_image: {e}")
        finally:
            cv2.destroyAllWindows()
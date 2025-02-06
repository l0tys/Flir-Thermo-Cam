# Library imports
import asyncio
import time
import cv2
import numpy as np

# File imports
from .data_buffer import get_buffered_data

current_position = (0, 0)


def update_temp_on_hover(event, x, y, flags, param):
    global current_position
    if event == cv2.EVENT_MOUSEMOVE:
        current_position = (x, y)


async def data_to_image() -> None:
    cv2.namedWindow("Processed Image")
    cv2.setMouseCallback("Processed Image", update_temp_on_hover)

    try:
        while True:
            start_time = time.time()

            buffer = get_buffered_data()

            if not buffer:
                print("Warning: No buffered data available.")
                await asyncio.sleep(1)
                continue

            data = buffer[-1]

            matrix = 0.0107143 * data - 44.2857
            matrix_norm = cv2.normalize(matrix, None, 0, 255, cv2.NORM_MINMAX)

            if matrix_norm is None or matrix_norm.size == 0:
                print("Warning: Normalized matrix is empty.")
                await asyncio.sleep(1)
                continue

            matrix_norm = np.uint8(matrix_norm)
            heatmap = cv2.applyColorMap(matrix_norm, cv2.COLORMAP_JET)

            overlay = heatmap.copy()

            if 'current_position' in globals():
                x, y = current_position
                if 0 <= y < matrix.shape[0] and 0 <= x < matrix.shape[1]:
                    temp = matrix[y, x]
                    cv2.putText(overlay, f"Temp: {temp:.2f} C", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

            cv2.imshow("Processed Image", overlay)

            if cv2.waitKey(1) == 27:
                break

            end_time = time.time()
            print(
                f"Data visualization execution time: {end_time - start_time:.2f} seconds")

            await asyncio.sleep(0)

    except Exception as e:
        print(f"Error in data_to_image: {e}")

    finally:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    asyncio.run(data_to_image())

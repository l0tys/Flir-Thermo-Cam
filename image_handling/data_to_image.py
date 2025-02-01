# Library imports
import asyncio
import cv2
import numpy as np

# File imports
from constants import DATA_PATH, DATA_TO_IMAGE_PATH


def update_temp_on_hover(event, x, y, flags, param):
    global current_position
    if event == cv2.EVENT_MOUSEMOVE:
        current_position = (x, y)


async def data_to_image(data_path=DATA_PATH, save_path=DATA_TO_IMAGE_PATH) -> None:
    data = np.loadtxt(data_path)

    global matrix
    matrix = 0.0466667 * data - 49

    matrix_norm = cv2.normalize(matrix, None, 0, 255, cv2.NORM_MINMAX)
    matrix_norm = np.uint8(matrix_norm)
    global heatmap
    heatmap = cv2.applyColorMap(matrix_norm, cv2.COLORMAP_JET)

    cv2.imwrite(save_path, heatmap)

    cv2.namedWindow("Processed Image")
    cv2.setMouseCallback("Processed Image", update_temp_on_hover)

    while True:
        overlay = heatmap.copy()

        if 'current_position' in globals():
            x, y = current_position
            temp = matrix[y, x]
            cv2.putText(overlay, f"Temp: {temp:.2f} C", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow("Processed Image", overlay)

        if cv2.waitKey(1) == 27:
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    asyncio.run(data_to_image())

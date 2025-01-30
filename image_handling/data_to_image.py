import cv2
import numpy as np
import os


def visualize_data(data_path, save_path, temp_min=0, temp_max=100):
    matrix = np.loadtxt(data_path)

    matrix_norm = cv2.normalize(
        matrix, None, temp_min, temp_max, cv2.NORM_MINMAX)
    matrix_norm = np.uint8(matrix_norm)
    heatmap = cv2.applyColorMap(matrix_norm, cv2.COLORMAP_JET)

    cv2.imwrite(save_path, heatmap)


if __name__ == "__main__":
    WORKING_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

    TEST_DATA_TO_IMAGE_SAVE_PATH = (
        WORKING_DIRECTORY + "/test_data/data_image.jpg")
    TEST_DATA_SAVE_PATH = (WORKING_DIRECTORY + "/test_data/data.txt")

    visualize_data(data_path=TEST_DATA_SAVE_PATH,
                   save_path=TEST_DATA_TO_IMAGE_SAVE_PATH, temp_min=20, temp_max=200)

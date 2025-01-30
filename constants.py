import os

WORKING_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

IMAGE_SAVE_PATH = os.path.join(
    WORKING_DIRECTORY, "/data/test_images/test_image.jpg")
DATA_TO_IMAGE_SAVE_PATH = os.path.join(
    WORKING_DIRECTORY, "/data/test_images/data_image.jpg")
DATA_SAVE_PATH = (WORKING_DIRECTORY + "/data/test_data/data.txt")

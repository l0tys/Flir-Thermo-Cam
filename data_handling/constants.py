# Library imports
import os

# Root working directory
WORKING_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Raw data
DATA_PATH = os.path.join(WORKING_DIRECTORY, "data", "raw_data", "raw_data.txt")

# Images
IMAGE_PATH = os.path.join(WORKING_DIRECTORY, "data", "images", "raw_image.jpg")
DATA_TO_IMAGE_PATH = os.path.join(
    WORKING_DIRECTORY, "data", "images", "processed_image.jpg")

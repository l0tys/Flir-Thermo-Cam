# Library imports
import os

# Root working directory
WORKING_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Calibration file
CALIBRATION_FILE_PATH = os.path.join(
    WORKING_DIRECTORY, "calibration/calibration.nuc")

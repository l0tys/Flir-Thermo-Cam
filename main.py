# Library imports
import sys
import asyncio
import PySpin

# File imports
from image_handling import capture_data, data_to_image

try:
    system = PySpin.System.GetInstance()
    cam_list = system.GetCameras()
    num_cameras = cam_list.GetSize()

    print(f"Number of cameras detected: {num_cameras}")

    if num_cameras == 0:
        print("No cameras detected. Exiting program.")
        cam_list.Clear()
        system.ReleaseInstance()
        sys.exit(1)

    cam = cam_list.GetByIndex()

    # Captures the image and saves it and its raw data as a matrix to data.txt
    asyncio.run(capture_data(cam=cam))

    # Proccesses the raw data from data.txt and converts it to a image
    asyncio.run(data_to_image())

    cam_list.Clear()
    system.ReleaseInstance()
except PySpin.SpinnakerException as ex:
    print(f"Error: {ex}")
    sys.exit(1)

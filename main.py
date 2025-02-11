# Library imports
import sys
import asyncio
import PySpin

# File imports
from data_handling import capture_data, data_to_image
from calibration import set_calibration, get_all_nodes
from util_functions import timer


@timer
async def main() -> None:
    system = None
    cam_list = None
    cam = None
    dev_mode = True

    try:
        system = PySpin.System.GetInstance()
        cam_list = system.GetCameras()
        num_cameras = cam_list.GetSize()

        print(f"Number of cameras detected: {num_cameras}")

        if num_cameras == 0:
            raise Exception("No cameras detected")

        cam = cam_list.GetByIndex(0)

        # Gets all the available nodes for calibration
        if dev_mode:
            if not get_all_nodes(cam=cam):
                raise Exception("Failed getting all nodes")

        # Sets the calibration
        if not set_calibration(cam=cam):
            raise Exception("Calibration failed")

        # Captures the image and saves it and its raw data as a matrix to data.txt
        capture_task = asyncio.create_task(capture_data(cam=cam))
        # Processes the raw data and converts it to an image
        image_task = asyncio.create_task(data_to_image())

        await asyncio.gather(capture_task, image_task)

    except PySpin.SpinnakerException as ex:
        print(f"Spinnaker Exception: {ex}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}, exiting program")
        sys.exit(1)

    finally:
        if cam is not None:
            try:
                cam.EndAcquisition()
            except PySpin.SpinnakerException:
                pass

            cam.DeInit()
            del cam

        if cam_list is not None:
            cam_list.Clear()

        if system is not None:
            system.ReleaseInstance()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exiting program")

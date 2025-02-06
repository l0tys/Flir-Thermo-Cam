# Library imports
import sys
import asyncio
import PySpin

# File imports
from data_handling import capture_data, data_to_image
from calibration import set_calibration


async def main() -> None:
    cam = None
    system = None
    cam_list = None

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

        cam = cam_list.GetByIndex(0)

        if set_calibration(cam=cam):
            print("Calibration applied successfully")
        else:
            print("Failed to apply calibration")

        # Captures the image and saves it and its raw data as a matrix to data.txt
        capture_task = asyncio.create_task(capture_data(cam=cam))
        # Processes the raw data from data.txt and converts it to an image
        image_task = asyncio.create_task(data_to_image())

        await asyncio.gather(capture_task, image_task)

    except PySpin.SpinnakerException as ex:
        print(f"Spinnaker Exception: {ex}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
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


asyncio.run(main())

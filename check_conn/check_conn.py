import PySpin
import sys


def check_connection():
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

        cam_list.Clear()
        system.ReleaseInstance()
    except Exception as e:
        print(f"An exception occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    check_connection()

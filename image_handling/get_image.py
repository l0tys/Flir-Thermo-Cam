import PySpin
import cv2
import numpy as np


def capture_and_save_heatmap(save_path, text_path, cam_index=0, temp_min=0, temp_max=100):
    system = PySpin.System.GetInstance()
    cam_list = system.GetCameras()
    num_cameras = cam_list.GetSize()

    if num_cameras == 0:
        print("No cameras detected. Please check your connection.")
        cam_list.Clear()
        system.ReleaseInstance()
        return False

    if cam_index >= num_cameras:
        print(
            f"Invalid camera index: {cam_index}. Only {num_cameras} cameras detected.")
        cam_list.Clear()
        system.ReleaseInstance()
        return False

    cam = cam_list.GetByIndex(cam_index)

    try:
        cam.Init()
        nodemap = cam.GetNodeMap()

        cam.BeginAcquisition()
        image = cam.GetNextImage()

        if image.IsIncomplete():
            print(f"Image incomplete with status {image.GetImageStatus()}")
        else:
            np_image = np.array(image.GetData(), dtype=np.uint8)
            np_image = np_image.reshape((image.GetHeight(), image.GetWidth()))

            norm_image = cv2.normalize(
                np_image, None, temp_min, temp_max, cv2.NORM_MINMAX)

            heatmap = cv2.applyColorMap(
                norm_image.astype(np.uint8), cv2.COLORMAP_BONE)

            cv2.imwrite(save_path, heatmap)
            print(f"Heatmap image saved to {save_path}")

            np.savetxt(text_file_path, norm_image, fmt='%.2f')
            print(f"Temperature values matrix saved to {text_file_path}")

        image.Release()
        cam.EndAcquisition()

    except PySpin.SpinnakerException as ex:
        print(f"Error: {ex}")
        if 'image' in locals():
            image.Release()
        cam.EndAcquisition()
        cam.DeInit()
        del cam
        cam_list.Clear()
        system.ReleaseInstance()
        return False

    finally:
        if cam.IsInitialized():
            cam.DeInit()
        del cam
        cam_list.Clear()
        system.ReleaseInstance()

    return True

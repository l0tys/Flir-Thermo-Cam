import PySpin
import cv2
import numpy as np


def test_capture_and_save_heatmap(save_path, text_file_path, cam_index=0, temp_min=None, temp_max=None):
    system = PySpin.System.GetInstance()
    cam_list = system.GetCameras()
    num_cameras = cam_list.GetSize()

    if num_cameras == 0:
        print("No cameras detected. Please check your connection.")
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

        # Ensure the correct pixel format (16-bit for temperature data)
        pixel_format = PySpin.CEnumerationPtr(nodemap.GetNode("PixelFormat"))
        if PySpin.IsAvailable(pixel_format) and PySpin.IsWritable(pixel_format):
            pixel_format.SetIntValue(PySpin.PixelFormat_Mono16)

        cam.BeginAcquisition()
        image = cam.GetNextImage()

        if image.IsIncomplete():
            print(f"Image incomplete with status {image.GetImageStatus()}")
        else:
            # Convert image to NumPy array (16-bit)
            np_image = np.array(image.GetData(), dtype=np.uint16)
            np_image = np_image.reshape((image.GetHeight(), image.GetWidth()))

            # Apply FLIR scaling factor (FLIR cameras typically use a scale factor of 100)
            scale_factor = 100.0  # Check your camera's documentation for the exact factor
            kelvin_image = np_image / scale_factor  # Convert raw values to Kelvin

            # Auto-scale temp_min and temp_max if not provided
            if temp_min is None:
                temp_min = np.min(kelvin_image)
            if temp_max is None:
                temp_max = np.max(kelvin_image)

            # Normalize and apply heatmap
            norm_image = cv2.normalize(
                kelvin_image, None, 0, 255, cv2.NORM_MINMAX)
            heatmap = cv2.applyColorMap(
                norm_image.astype(np.uint8), cv2.COLORMAP_JET)

            # Save heatmap image
            cv2.imwrite(save_path, heatmap)
            print(f"Heatmap image saved to {save_path}")

            # Save raw temperature data in Kelvin
            np.savetxt(text_file_path, kelvin_image, fmt='%.2f')
            print(f"Temperature values matrix saved to {text_file_path}")

        # Cleanup
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

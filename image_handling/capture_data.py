# Library imports
import PySpin
import cv2
import numpy as np
import asyncio

# File imports
from .constants import IMAGE_PATH, DATA_PATH


async def capture_data(cam, save_path=IMAGE_PATH, text_path=DATA_PATH) -> None:
    try:
        cam.Init()

        cam.BeginAcquisition()
        image = cam.GetNextImage()

        if image.IsIncomplete():
            print(f"Image incomplete with status {image.GetImageStatus()}")
        else:
            pixel_format = image.GetPixelFormat()
            is_16bit = pixel_format in [
                PySpin.PixelFormat_Mono16, PySpin.PixelFormat_BGR16]
            dtype = np.uint16 if is_16bit else np.uint8  # Choose correct data type

            np_image = np.array(image.GetData(), dtype=dtype)
            np_image = np_image.reshape((image.GetHeight(), image.GetWidth()))

            # Convert raw values to absolute temperature in Kelvin
            norm_image = np_image

            # Scale for visualization
            vis_image = cv2.normalize(
                norm_image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            heatmap = cv2.applyColorMap(vis_image, cv2.COLORMAP_JET)

            cv2.imwrite(save_path, heatmap)
            print(f"Heatmap image saved to {save_path}")

            # Save absolute temperature values in Kelvin
            np.savetxt(text_path, norm_image, fmt='%.2f')

            # Remove the first line
            with open(text_path, 'r') as file:
                lines = file.readlines()[1:]  # Skip the first line

            # Overwrite the file without the first line
            with open(text_path, 'w') as file:
                file.writelines(lines)

            print(
                f"Temperature values matrix saved to {text_path} (without first line)")

        image.Release()  # Ensure image is released

    except PySpin.SpinnakerException as ex:
        print(f"Error: {ex}")

    finally:
        if cam is not None:
            try:
                cam.EndAcquisition()
            except PySpin.SpinnakerException:
                pass

            cam.DeInit()
            del cam

    return True

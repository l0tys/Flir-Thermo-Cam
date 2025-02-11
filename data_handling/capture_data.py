# Library imports
import PySpin
import numpy as np
import asyncio

# File imports
from .data_buffer import data_buffer


async def capture_data(cam, buffer=data_buffer) -> None:
    try:
        cam.Init()
        cam.BeginAcquisition()

        while True:
            try:
                image = cam.GetNextImage()

                if image.IsIncomplete():
                    print(
                        f"Image incomplete with status {image.GetImageStatus()}")
                else:
                    pixel_format = image.GetPixelFormat()

                    is_16bit = pixel_format in [
                        PySpin.PixelFormat_Mono16, PySpin.PixelFormat_BGR16]
                    dtype = np.uint16 if is_16bit else np.uint8

                    np_image = np.frombuffer(image.GetData(), dtype=dtype).reshape(
                        image.GetHeight(), image.GetWidth())

                    buffer.add(np_image[1:])

                image.Release()

                await asyncio.sleep(0)

            except asyncio.CancelledError:
                print("Capture loop stopped.")
                break

    except PySpin.SpinnakerException as ex:
        print(f"Error: {ex}")

    finally:
        cam.EndAcquisition()
        cam.DeInit()

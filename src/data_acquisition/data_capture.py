# * Library imports
import PySpin
import numpy as np
import asyncio

# * File imports
from ..data_buffer import raw_data_buffer

class DataCapture:
    def __init__(self, camera: PySpin.Camera, data_buffer = raw_data_buffer):
        self.camera = camera
        self.data_buffer = data_buffer

    async def data_capture(self):
        try:
            try:
                self.camera.Init()
                self.camera.BeginAcquisition()

                while True:
                    try:
                        image = self.camera.GetNextImage()

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

                            isinstance(np_image, np.ndarray)

                            self.data_buffer.add(np_image[1:])

                        image.Release()

                        await asyncio.sleep(0)

                    except asyncio.CancelledError:
                        print("Capture loop stopped.")
                        break

            except PySpin.SpinnakerException as ex:
                print(f"Error: {ex}")

            finally:
                self.camera.EndAcquisition()
                self.camera.DeInit()
        except asyncio.CancelledError:
            pass

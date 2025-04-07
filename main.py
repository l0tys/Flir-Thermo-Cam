# * Library imports
import sys
import asyncio
import PySpin

# * File imports
from calibration import set_calibration, get_all_nodes
from data_acquisition import DataCapture
from data_handling import ProcessData, DataCumulated
from data_visualization import DataToImage, DataAverage

class Camera:
    def __init__(self):
        self.system: any = PySpin.System.GetInstance()
        self.camera_list: any = self.system.GetCameras()
        self.camera: any = self.camera_list.GetByIndex(0) if self.camera_list.GetSize() > 0 else None
        self.dev_mode: bool = False

        self.data_capture = DataCapture(camera=self.camera)
        self.data_image = DataToImage()
        self.data_process = ProcessData()
        self.data_average = DataAverage()
        self.data_cumulated = DataCumulated()

    async def main(self):
        try:
            # Gets the amount of cameras available
            num_cameras = self.camera_list.GetSize()

            print(f"Number of cameras detected: {num_cameras}")

            if num_cameras == 0:
                raise Exception("No cameras detected")

            # Gets all the available nodes for calibration
            if self.dev_mode:
                if not get_all_nodes(cam=self.camera):
                    raise Exception("Failed getting all nodes")

            # Sets the calibration
            if not set_calibration(cam=self.camera):
                raise Exception("Calibration failed")

            # Captures the image and saves it and its raw data as a matrix to data.txt
            capture_task = asyncio.create_task(self.data_capture.data_capture())
            # Processes the raw data and saves it to the processed buffer
            process_task = asyncio.create_task(self.data_process.process_data())
            # Processes the raw data and converts it to an image
            image_task = asyncio.create_task(self.data_image.data_to_image())
            # Displays the average temperature in a chart
            data_average_task = asyncio.create_task(self.data_average.data_chart())
            # Displays the accumulated temperature in a chart
            # data_cumulated_task = asyncio.create_task(self.data_cumulated.data_cumulated())

            await asyncio.gather(capture_task, process_task, image_task, data_average_task)

        except PySpin.SpinnakerException as ex:
            print(f"Spinnaker Exception: {ex}")
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}, exiting program")
            sys.exit(1)
        except asyncio.CancelledError:
            pass
        finally:
            try:
                if self.camera is not None:
                    if self.camera.IsStreaming():
                        self.camera.EndAcquisition()
                    self.camera.DeInit()
                    del self.camera
                    self.camera = None
            except PySpin.SpinnakerException as ex:
                print(f"Error during camera cleanup: {ex}")

            try:
                if self.camera_list is not None:
                    self.camera_list.Clear()
                    del self.camera_list
                    self.camera_list = None
            except PySpin.SpinnakerException as ex:
                print(f"Error during camera list cleanup: {ex}")

            try:
                if self.system is not None:
                    self.system.ReleaseInstance()
                    del self.system
                    self.system = None
            except PySpin.SpinnakerException as ex:
                print(f"Error during system cleanup: {ex}")

if __name__ == "__main__":
    try:
        camera = Camera()
        asyncio.run(camera.main())
    except KeyboardInterrupt:
        print("Exiting program")

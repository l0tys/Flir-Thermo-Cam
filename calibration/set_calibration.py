# Library imports
import PySpin


def set_calibration(cam) -> bool:
    try:
        cam.Init()

        nodemap = cam.GetNodeMap()
        nodes = nodemap.GetNodes()

        print(f"Nodemap: {nodemap}")

        for node in nodes:
            print(node)

        # Set Width
        try:
            width = PySpin.CIntegerPtr(nodemap.GetNode("Width"))
            if PySpin.IsAvailable(width) and PySpin.IsWritable(width):
                width.SetValue(640)
            else:
                print("Width parameter not available or writable.")
        except PySpin.SpinnakerException as e:
            print(f"Spinnaker Exception: {e}")

        # Set Height
        try:
            height = PySpin.CIntegerPtr(nodemap.GetNode("Height"))
            if PySpin.IsAvailable(height) and PySpin.IsWritable(height):
                height.SetValue(513)
            else:
                print("Height parameter not available or writable.")
        except PySpin.SpinnakerException as e:
            print(f"Spinnaker Exception: {e}")

        # Set Offset X
        try:
            offset_x = PySpin.CIntegerPtr(nodemap.GetNode("OffsetX"))
            if PySpin.IsAvailable(offset_x) and PySpin.IsWritable(offset_x):
                offset_x.SetValue(0)
            else:
                print("OffsetX parameter not available or writable.")
        except PySpin.SpinnakerException as e:
            print(f"Spinnaker Exception: {e}")

        # Set Offset Y
        try:
            offset_y = PySpin.CIntegerPtr(nodemap.GetNode("OffsetY"))
            if PySpin.IsAvailable(offset_y) and PySpin.IsWritable(offset_y):
                offset_y.SetValue(0)
            else:
                print("OffsetY parameter not available or writable.")
        except PySpin.SpinnakerException as e:
            print(f"Spinnaker Exception: {e}")

        # Set the calibration tag
        try:
            set_calibration_tag = PySpin.CStringPtr(
                nodemap.GetNode("PS0CalibrationLoadTag"))
            if PySpin.IsReadable(set_calibration_tag):
                print(f"Float: {set_calibration_tag.GetValue()}")
                set_calibration_tag.SetValue("25mm, Empty, 35C - 150C")

            print(set_calibration_tag.GetValue())

        except PySpin.SpinnakerException as e:
            print(f"Spinnaker Exception: {e}")

        # Reads the camera tmperature
        try:
            camera_temperature = PySpin.CFloatPtr(
                nodemap.GetNode("DeviceTemperature"))
            if not PySpin.IsAvailable(camera_temperature) or not PySpin.IsReadable(camera_temperature):
                print("Unable to read temperature. Aborting...")

            temperature_value = camera_temperature.GetValue()
            print(f"Camera Internal Temperature: {temperature_value} °C")
        except PySpin.SpinnakerException as e:
            print(f"Spinnaker Exception: {e}")

        cam.DeInit()

        cam.Init()

        print("Calibration parameters set successfully.")
        return True
    except PySpin.SpinnakerException as ex:
        print(f"Error: {ex}")
        return False

# Library imports
import PySpin


def set_calibration(cam):
    try:
        cam.Init()

        nodemap = cam.GetNodeMap()

        print(f"Nodemap: {nodemap}")

        # Set Width
        width = PySpin.CIntegerPtr(nodemap.GetNode("Width"))
        if PySpin.IsAvailable(width) and PySpin.IsWritable(width):
            width.SetValue(640)
        else:
            print("Width parameter not available or writable.")

        # Set Height
        height = PySpin.CIntegerPtr(nodemap.GetNode("Height"))
        if PySpin.IsAvailable(height) and PySpin.IsWritable(height):
            height.SetValue(513)
        else:
            print("Height parameter not available or writable.")

        # Set Offset X
        offset_x = PySpin.CIntegerPtr(nodemap.GetNode("OffsetX"))
        if PySpin.IsAvailable(offset_x) and PySpin.IsWritable(offset_x):
            offset_x.SetValue(0)
        else:
            print("OffsetX parameter not available or writable.")

        # Set Offset Y
        offset_y = PySpin.CIntegerPtr(nodemap.GetNode("OffsetY"))
        if PySpin.IsAvailable(offset_y) and PySpin.IsWritable(offset_y):
            offset_y.SetValue(0)
        else:
            print("OffsetY parameter not available or writable.")

        print("Calibration parameters set successfully.")
        cam.DeInit()

        cam.Init()

        return True
    except PySpin.SpinnakerException as ex:
        print(f"Error: {ex}")
        return False

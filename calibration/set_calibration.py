# Library imports
import PySpin

# File imports
from .constants import CALIBRATION_FILE_PATH


def set_calibration(cam):
    try:
        cam.Init()

        nodemap = cam.GetNodeMap()
        print(f"Nodemap: {nodemap}")

        print(f"Loading NUC file from: {CALIBRATION_FILE_PATH}")
        with open(CALIBRATION_FILE_PATH, 'rb') as nuc_file:
            nuc_data = nuc_file.read()

        node_nuc_table = PySpin.CCommandPtr(nodemap.GetNode("NucTableControl"))
        if not PySpin.IsAvailable(node_nuc_table) or not PySpin.IsWritable(node_nuc_table):
            print("NUC table control node is not available or writable.")
            return False

        node_nuc_table.Execute()

        node_nuc_data = PySpin.CRegisterPtr(nodemap.GetNode("NucTableData"))
        if not PySpin.IsAvailable(node_nuc_data) or not PySpin.IsWritable(node_nuc_data):
            print("NUC table data node is not available or writable.")
            return False

        node_nuc_data.SetValue(nuc_data)

        print("Calibration parameters set successfully.")
        return True
    except PySpin.SpinnakerException as ex:
        print(f"Error: {ex}")
        return False

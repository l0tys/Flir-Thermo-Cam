import PySpin

def set_node_value(nodemap, node_name, value, node_type):
    try:
        node = node_type(nodemap.GetNode(node_name))
        if PySpin.IsAvailable(node) and PySpin.IsWritable(node):
            node.SetValue(value)
        else:
            print(f"{node_type}: {node_name} parameter not available or writable.")
    except PySpin.SpinnakerException as e:
        print(f"Spinnaker Exception ({node_name}): {e}")

def set_calibration(cam: PySpin.Camera) -> bool:
    try:
        cam.Init()
        nodemap = cam.GetNodeMap()

        int_params = {
            "Width": 640,
            "Height": 513,
            "OffsetX": 0,
            "OffsetY": 0,
        }

        float_params = {}

        str_params = {
            # "PS0CalibrationLoadTag": "25mm, Empty, 35C - 150C"
        }

        bool_params = {}

        with open("calibration/params/cal_params.txt", "r") as param_file:
            for line in param_file:
                parts = line.strip().split(" ")
                if len(parts) >= 3:
                    data_type = parts[0]
                    name = parts[1]
                    value = " ".join(parts[2:])

                    if data_type == "Integer":
                        int_params[name] = int(value)
                    elif data_type == "Float":
                        float_params[name] = float(value)
                    # elif data_type == "String":
                    #     str_params[name] = value
                    # elif data_type == "bool":
                    #     bool_params[name] = bool(value)

        for param, value in int_params.items():
            set_node_value(nodemap=nodemap, node_name=param, value=value, node_type=PySpin.CIntegerPtr)
        for param, value in float_params.items():
            set_node_value(nodemap=nodemap, node_name=param, value=value, node_type=PySpin.CFloatPtr)
        for param, value in str_params.items():
            set_node_value(nodemap=nodemap, node_name=param, value=value, node_type=PySpin.CStringPtr)
        for param, value in bool_params.items():
            set_node_value(nodemap=nodemap, node_name=param, value=value, node_type=PySpin.CBooleanPtr)

        try:
            temperature_node = PySpin.CFloatPtr(nodemap.GetNode("DeviceTemperature"))
            if PySpin.IsAvailable(temperature_node) and PySpin.IsReadable(temperature_node):
                print(f"Camera Internal Temperature: {temperature_node.GetValue()} °C")
            else:
                print("Unable to read temperature.")
        except PySpin.SpinnakerException as e:
            print(f"Spinnaker Exception (DeviceTemperature): {e}")

        cam.DeInit()
        cam.Init()
        print("Calibration parameters set successfully.")

        return True
    except PySpin.SpinnakerException as ex:
        print(f"Error: {ex}")
        return False
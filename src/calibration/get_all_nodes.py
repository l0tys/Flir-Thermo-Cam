# Library imports
import PySpin


def get_all_nodes(cam: PySpin.Camera) -> bool:
    try:
        cam.Init()

        nodemap = cam.GetNodeMap()
        nodes = nodemap.GetNodes()

        print(f"Nodemap: {nodemap}")
        open("params/30_150_all_nodes_25mm.txt", "w").close()

        with open("params/30_150_all_nodes_25mm.txt", "a") as file:
            for node in nodes:
                if PySpin.IsAvailable(node) and PySpin.IsWritable(node):
                    node_name = node.GetName()
                    node_type = None
                    node_value = None

                    if PySpin.IsReadable(node):
                        if node.GetPrincipalInterfaceType() == PySpin.intfIFloat:
                            node_type = "float"
                            node_value = PySpin.CFloatPtr(node).GetValue()
                        elif node.GetPrincipalInterfaceType() == PySpin.intfIInteger:
                            node_type = "int"
                            node_value = PySpin.CIntegerPtr(node).GetValue()
                        elif node.GetPrincipalInterfaceType() == PySpin.intfIString:
                            node_type = "str"
                            node_value = PySpin.CStringPtr(node).GetValue()
                        elif node.GetPrincipalInterfaceType() == PySpin.intfIBoolean:
                            node_type = "bool"
                            node_value = PySpin.CBooleanPtr(node).GetValue()
                        elif node.GetPrincipalInterfaceType() == PySpin.intfIEnumeration:
                            node_type = "enum"
                            node_value = PySpin.CEnumerationPtr(node).GetCurrentEntry().GetSymbolic()
                        elif node.GetPrincipalInterfaceType() == PySpin.intfICommand:
                            node_value = "Command Node (No Value)"
                        else:
                            node_value = "Unsupported Node Type"

                    file.write(f"{node_type} {node_name} {node_value}\n")
        cam.DeInit()

        print("Successfully gotten all nodes")
        return True
    except PySpin.SpinnakerException as ex:
        print(f"Error: {ex}")
        return False

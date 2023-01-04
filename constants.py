
# Constant variables
SERVICE_NAME = "org.bluez"
ADAPTER_INTERFACE = SERVICE_NAME + ".Adapter1"
BUS_NAME = 'org.bluez'
D_BUS_OBJECT_MANAGER = "org.freedesktop.DBus.ObjectManager"
D_BUS_PROPERTIES = "org.freedesktop.DBus.Properties"
DEVICE_INTERFACE = SERVICE_NAME + ".Device1"
ROOT = "/"

#  Global variables used
ADAPTER_OBJ = "NULL" # To hold the selected Object
current_connected_object = "NULL" # Holds current connected object/Path
current_connected_interface_device1 = "NULL" # Holds current\
                                    # connected object's Interface
list_of_scanned_devices = {} # To hold the list of scanned devices
list_of_pair_device = [] # To hold the list of paired devices
pulseaudio_daemon = "NULL"
def selected_dongle():
    """
    whenever the other modules required the current
    selected dongle can use this as a function.
    """
    return ADAPTER_OBJ





import constants as gl
import dbus
import dbus.mainloop.glib
from logger_mod import *
try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject
import time
import utils as convert

bus = dbus.SystemBus()

class GapLib:

    def __init__(self):
        """ Constructor: This will init all the instance variable
        once the gaplib class is called.
        """
        # Public class member.
        self.dictionary_for_scanned_devices = {}
        # Private class member.
        self.__adapter_obj = gl.ADAPTER_OBJ
        self.__root_obj_manager_iface = dbus.Interface\
            (bus.get_object(gl.BUS_NAME, gl.ROOT), gl.D_BUS_OBJECT_MANAGER)
        self.__adapter_obj_proxy = bus.get_object(gl.BUS_NAME, gl.ADAPTER_OBJ)
        self.__adapter_DBUS_interface = dbus.Interface\
            (self.__adapter_obj_proxy, gl.D_BUS_PROPERTIES)

    @property
    def powered(self):
        """
        This method will return the power status of the adapter.
        Arguments: None
        Returns: Powered status
        """
        powered = self.__adapter_DBUS_interface.\
            Get(gl.ADAPTER_INTERFACE, "Powered")
        return str(powered)

    @property
    def address(self):
        """
        This method will return the address of the adapter.
        Arguments: None
        Returns: Bluetooth device address
        """
        Address = self.__adapter_DBUS_interface.Get\
            (gl.ADAPTER_INTERFACE, "Address")
        return str(Address)

    @property
    def address_type(self):
        """
        This method will return the adddressType of the adapter.
        Arguments: None
        Returns: Bluetooth address type
        """
        Address_type = self.__adapter_DBUS_interface.Get\
            (gl.ADAPTER_INTERFACE, "AddressType")
        return str(Address_type)

    @property
    def alias(self):
        """
        This method will return the alias name of the adapter.
        Arguments: None
        Returns: Bluetooth friendly name
        """
        Alias = self.__adapter_DBUS_interface.Get(gl.ADAPTER_INTERFACE, "Alias")
        return str(Alias)

    @property
    def name(self):
        """
        This method will return the user friendly name of the adapter.
        Arguments: None
        Returns: Bluetooth system name
        """
        Name = self.__adapter_DBUS_interface.Get(gl.ADAPTER_INTERFACE, "Name")
        return str(Name)

    @property
    def class_of_device(self):
        """
        This method will return the class of the adapter.
        Arguments: None
        Returns: Bluetooth class of device
        """
        Class = self.__adapter_DBUS_interface.Get(gl.ADAPTER_INTERFACE, "Class")
        return str(Class)

    @property
    def discoverabletimeout(self):
        """
        This method will return the Discoverable Timeout value.
        Arguments: None
        Returns: Discoverable timeout in seconds
        """
        DiscoverableTimeout = self.__adapter_DBUS_interface.Get\
            (gl.ADAPTER_INTERFACE, "DiscoverableTimeout")
        return str(DiscoverableTimeout)

    @property
    def pairabletimeout(self):
        """
        This method will return the pairable Timeout value.
        Arguments: None
        Returns: Pairable timeout in seconds
        """
        PairableTimeout = self.__adapter_DBUS_interface.Get\
            (gl.ADAPTER_INTERFACE, "PairableTimeout")
        return str(PairableTimeout)

    def start_scan(self,duration=0):
        """
        This method is to start the scan operation
        Arguments:-
                Duration in "Sec's"
                If the user does not provide any time duration in "sec" ,
                by default the duration is set as Zero meaning that
                the device is scanning till user enters the option Stop scan
        Returns:-
                list of scanned devices
        """
        self.dictionary_for_scanned_devices.clear()
        
        objects = self.__root_obj_manager_iface.GetManagedObjects()
        path_prefix = gl.ADAPTER_OBJ

        for path, interface in objects.items():

            if path == path_prefix:
                obj = bus.get_object(gl.SERVICE_NAME, path)
                adapter_iface = dbus.Interface(obj, gl.ADAPTER_INTERFACE)

                try:
                    adapter_iface.StartDiscovery()
                    log.info(" Scanning Started! ")
                except Exception as e:
                    log.critical(e)
                    log.info(" Failed to Start "
                                    "the Discovery!")
                    return False
                break

        if duration:
            time.sleep(duration)
            adapter_iface.StopDiscovery()
            log.info("Scanning completed after {} Sec".format(str(duration)))
            log.info("*"*100)
            new_objects = self.__root_obj_manager_iface.GetManagedObjects()
            path_prefix = gl.ADAPTER_OBJ + "/dev_"
            self.dictionary_for_scanned_devices.clear()

            for path, iface in new_objects.items():
                if path_prefix in path:
                    obj = bus.get_object(gl.SERVICE_NAME, path)
                    device_iface = dbus.Interface(obj,gl.D_BUS_PROPERTIES)

                    name = device_iface.Get(gl.DEVICE_INTERFACE, "Alias")
                    addr = device_iface.Get(gl.DEVICE_INTERFACE, "Address")
                    self.dictionary_for_scanned_devices[name] = addr

            return self.dictionary_for_scanned_devices
        return False

    def stop_scan(self):
        """
         This method is to stop the scan operation
         Arguments:-
                    None
         Returns:-
                    list of scanned devices
        """
        objects = self.__root_obj_manager_iface.GetManagedObjects()
        path_prefix = gl.ADAPTER_OBJ

        for path, interface in objects.items():

            if path == path_prefix:
                obj = bus.get_object(gl.SERVICE_NAME, path)
                adapter_iface = dbus.Interface(obj, gl.ADAPTER_INTERFACE)
                try:
                    log.debug(" User tried to end the "
                                 "scan operation explicitly ")
                    adapter_iface.StopDiscovery()
                except Exception as e:
                    log.critical(e)
                    log.info("  Failed to execute the "
                                 "StopDiscovery api ")
                    return False
                log.info("scanning stopped! ")
                log.info("*"*100)
                break

        new_objects = self.__root_obj_manager_iface.GetManagedObjects()
        path_prefix = gl.ADAPTER_OBJ + "/dev_"
        self.dictionary_for_scanned_devices.clear()

        for path, iface in new_objects.items():
            if path_prefix in path:
                obj = bus.get_object(gl.SERVICE_NAME, path)
                device_iface = dbus.Interface(obj, gl.D_BUS_PROPERTIES)

                name = device_iface.Get(gl.DEVICE_INTERFACE, "Alias")
                addr = device_iface.Get(gl.DEVICE_INTERFACE, "Address")
                self.dictionary_for_scanned_devices[name] = addr

        return self.dictionary_for_scanned_devices

    def pair(self,request_name):
        """
        This method is to pair the device within the scanned devices
        Arguments:-
                name of the device which he is interested to pair,
                out of scanned devices
        Returns:-
                Boolean value:
                True: if the list of scanned devices is empty
                False: if the requested name to pair the device,
                is not in the "scanned device list".
        """
        value = bool(gl.list_of_scanned_devices)
        if value == 0:
            log.info(" No scanned Devices")
            return True

        check = 0
        for name,address in gl.list_of_scanned_devices.items():
            if name == request_name:
                bd_address = gl.list_of_scanned_devices[name]
                log.info(bd_address)
                check = 1
        if check == 0:
            return False

        path = convert.convert_colon_underscore_with_path\
            (bd_address, gl.ADAPTER_OBJ)
        proxy_obj = dbus.Interface\
            (bus.get_object(gl.SERVICE_NAME, path),gl.DEVICE_INTERFACE)

        try:
            log.info(" Pairing Initiated!!!..........")
            proxy_obj.Pair()
            log.info(" Paired Successfully! ")
        except Exception as e:
            log.critical(e)
            log.info(" Failed to pair the device")
            return True

    def device_paired(self):
        """
            This method is to check which devices are paired currently
            Arguments:-
                        None
            Returns:-
                    1.Boolean False:- If none of the devices are paired
                    2.List :- List of paired devices
        """
        log.debug(" User wants the list of "
                     "paired devices.")
        objects = self.__root_obj_manager_iface.GetManagedObjects()

        count = 0
        list_of_paired_device = []

        for path, iface in objects.items():

            if len(path) > 16 and len(path) <= 38:
                try:
                    proxy_obj = bus.get_object(gl.SERVICE_NAME, path)
                    adapter_iface = dbus.Interface\
                        (proxy_obj,gl.D_BUS_PROPERTIES)
                except Exception as e:
                    log.critical(e)

                try:
                    ret = adapter_iface.Get(gl.DEVICE_INTERFACE, "Paired")
                except Exception as e:
                    log.critical(e)

                if ret == 1:
                    count = 1
                    address = adapter_iface.Get(gl.DEVICE_INTERFACE, "Address")
                    list_of_paired_device.append(address)
        if count == 0:
            log.info(" No paired devices")
            return False

        return list_of_paired_device

    def connect(self,bd_address):
        """
            This method is to connect the device out of paired devices.
            Arguments:-
                        BD_ADDRESS of the device, which user is interested to connect.
            Returns:-
                        Boolean True: if the connection is successful
                        Boolean False: if the connection is refused
        """
        path = convert.convert_colon_underscore_with_path\
            (bd_address,gl.ADAPTER_OBJ)
        gl.current_connected_object = bus.get_object(gl.SERVICE_NAME, path)

        gl.current_connected_interface_device1 = dbus.Interface\
            (gl.current_connected_object, gl.DEVICE_INTERFACE)
        log.info(" Connecting........")

        try:
            log.debug("  Connection Initiated ")
            gl.current_connected_interface_device1.Connect()
            log.info(" Connected successfully"
                         " to the device  ")
            return True
        except Exception as e:
            log.critical(e)
            log.info(" Failed to connect the device")
            return False

    def disconnect(self):
        """
            This method is to disconnect the current connected device.
            Arguments:-
                        None
            Returns:-
                        Boolean True: Disconnected successful
                        Boolean False: Failed to disconnect the device
        """
        objects = self.__root_obj_manager_iface.GetManagedObjects()
        count = 0

        for path, iface in objects.items():

            if len(path) > 16 and len(path) <= 38:
                try:
                    proxy_obj = bus.get_object(gl.SERVICE_NAME, path)
                    adapter_iface = dbus.Interface\
                        (proxy_obj, gl.D_BUS_PROPERTIES)
                except Exception as e:
                    log.critical(e)
                    return

                try:
                    ret = adapter_iface.Get(gl.DEVICE_INTERFACE, "Connected")
                except Exception as e:
                    log.critical(e)
                    return

                if ret == 1:
                    count = 1
                    device_interface = dbus.Interface\
                        (proxy_obj, gl.DEVICE_INTERFACE)
                    try:
                        log.info(" Disconnect Initiated ")
                        device_interface.Disconnect()
                        log.info(" Disconnected successfully ")
                        return True
                    except Exception as e:
                        log.critical(e)
                        log.info(" Failed to disconnect "
                                        "the device")
                        return False

        if count == 0:
            log.info(" No device is connected ")

    def remove_device(self,bd_address):
        """
            This method is to remove the device out of paired devices
            Arguments:-
                        BD_ADDRESS of the particular device which user wants to remove
            Returns:-
                        Boolean True: Device removed Successful
                        Boolean False: Failed to remove to the device
        """
        path = convert.convert_colon_underscore_with_path\
            (bd_address, gl.ADAPTER_OBJ)

        try:
            proxy_for_adapter = dbus.Interface\
            (bus.get_object(gl.SERVICE_NAME, gl.ADAPTER_OBJ),gl.ADAPTER_INTERFACE)
            log.info(" Initiated to Remove the device!.............. ")
            proxy_for_adapter.RemoveDevice(path)
            log.info("  DEVICE: {} removed"
                         " successfully ".format(str(bd_address)))
            return True
        except Exception as e:
            log.critical(e)
            log.info("  Failed to remove "
                            "the device")
            return False

    def start_discovery(self):
        """
            This method is to set the dongle in discoverable mode.
            Arguments:-
                        None
            Returns:-
                        Boolean True: Set to discoverable Mode Successfully
                        Boolean False: Failed to Turn on the discoverable Mode
        """
        obj_proxy = bus.get_object(gl.BUS_NAME, gl.ADAPTER_OBJ)
        interface = dbus.Interface(obj_proxy, gl.D_BUS_PROPERTIES)

        try:
            value = dbus.Boolean(1)
            log.info(" Initiated to Set the"
                         " adapter in Discoverable mode")
            interface.Set(gl.ADAPTER_INTERFACE, "Discoverable", value)
            log.info(" Adapter set to discoverable mode")
            return True
        except Exception as e:
            log.critical(e)
            log.info(" Failed to set the adapter"
                            " in discoverable mode")
            return False

    def stop_discovery(self):
        """
            This method is to turn off the discoverable Mode.
            Arguments:-
                        None
            Returns:-
                        Boolean True: Turned off successfully
                        Boolean False: Failed to turn off
        """
        obj_proxy = bus.get_object(gl.BUS_NAME, gl.ADAPTER_OBJ)
        interface = dbus.Interface(obj_proxy, gl.D_BUS_PROPERTIES)

        try:
            value = dbus.Boolean(0)
            log.debug(" User trying to turn off "
                         "discoverable mode")
            interface.Set(gl.ADAPTER_INTERFACE, "Discoverable", value)
            log.info("  Removed from discoverable mode")
            return True
        except Exception as e:
            log.critical(e)
            log.info("  Failed to remove from "
                            "the discoverable mode ")
            return False

    def set_pairable_timeout(self,time):
        """
            This method is to set the pairable timeout
            Arguments:-
                    Time duration in seconds
            Returns:-
                    Boolean True: Pairabletimeout set successfully
                    Boolean False: Failed to set pairable timeout
        """
        try:
            time = dbus.UInt32(time)
            log.debug(" User trying to set the "
                         "pairable timeout value")
            self.__adapter_DBUS_interface.Set\
                (gl.ADAPTER_INTERFACE, "PairableTimeout", time)
            log.info("  pairable timeout"
                         " value set as: {}".format(time))
            return True
        except Exception as e:
            log.critical(e)
            log.info("  Failed to set the"
                         " pairable timeout value")
            return False

    def get_pairable_timeout(self):
        """
            This method is to Get the pairable timeout value
            Arguments:-
                        None
            Returns:-
                    1.Integer value: Time duration in seconds
                                (or)
                    2.Boolean False: If it fails to fetch the pairabletimeout value
        """
        try:
            log.debug("  User trying to get the"
                         " pairable timeout value")
            value = self.__adapter_DBUS_interface.Get\
                (gl.ADAPTER_INTERFACE, "PairableTimeout")
            log.info("User received the"
                         " pairable timeout value as: {}".format(value))
            return value
        except Exception as e:
            log.critical(e)
            log.info("  Failed to get the"
                            " pairable timeout value ")
            return False

    def set_Discoverable_timeout(self,time):
        """
            This method is to set the discoverable timeout value
            Arguments:-
                        Time duration in seconds
            Returns:-
                    Boolean True: Discoverable timeout value is set successfully
                    Boolean False: Failed to set the Discoverable timeout value
        """
        try:
            time = dbus.UInt32(time)
            log.debug(" User trying to set the"
                         " discoverable timeout value")
            self.__adapter_DBUS_interface.Set\
                (gl.ADAPTER_INTERFACE, "DiscoverableTimeout", time)
            log.info(" Discoverable timeout "
                         "value set as: {}".format(time))
            return True
        except Exception as e:
            log.critical(e)
            log.info("  Failed to set the "
                            "Discoverable timeout value ")
            return False

    def get_Discoverable_timeout(self):
        """
         This method is to Get the discoverable timeout value
            Arguments:-
                        None
            Returns:-
                    1.Integer value: time duration in seconds
                                (or)
                    2.Boolean False: If it fails to fetch the discoverable timeout value
        """
        try:
            log.debug("  User trying to get the "
                         "discoverale timeout value ")
            value = self.__adapter_DBUS_interface.Get\
                (gl.ADAPTER_INTERFACE, "DiscoverableTimeout")
            log.info("  Discoverable timeout "
                         "value: {}".format(value))
            return value
        except Exception as e:
            log.critical(e)
            log.info("  Failed to get the "
                            "discoverable timeout value")
            return False


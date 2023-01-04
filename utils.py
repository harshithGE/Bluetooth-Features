import datetime
import logging
import constants as gl
import dbus
import dbus.mainloop.glib
from logger_mod import  *
import os
from datetime import datetime
import subprocess
try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject
import sys

class Daemon:
    def __init__(self):
        """
        This constructor will create a new folder with timestramp,
        for each user entry a new folder wil be created.
        """
        pwd_path = os.getcwd()
        directory = "BT_logs"
        path = os.path.join(pwd_path,directory)
        try:
            os.mkdir(path)
        except:
            pass
        os.chdir('BT_logs')

        mydir = os.path.join(
            os.getcwd(),
            datetime.now().strftime('%-d_%b_%Y_%X_%p'))

        try:
            os.mkdir(mydir)
        except:
            pass
        os.chdir(mydir)

        # This object will holds the process that are running.
        self.__Process1 = "NULL" #Dbus-daemon
        self.__Process2 = "NULL" #Bluetoothd
        self.__Process3 = "NULL" #Pulseaudio
    def d_bus_daemon(self):
        """
        This method will run the `D-Bus` Daemons that helps other process to communicate
        Arguments: None
        Returns  : Object of Dbus-Daemon process
        """
        cmd = "/usr/local/bluez/dbus-1.12.20/bin/dbus-daemon --system --nopidfile"
        file_handler_dbus = open("dbus.log", 'a+')
        self.__Process1 = subprocess.Popen(cmd, shell=True, stdout=file_handler_dbus, stderr=file_handler_dbus)
        if self.__Process1.returncode == None:
            log.info("*"*100)
            log.info(" D-bus Daemon Initiated....")
        else:
            log.info(" Failed to init "'D-Bus Daemon'" ")
            sys.exit(1)
        return self.__Process1
    def bluetooth_d_daemon(self):
        """
        This method will run the `bluetooth-d` Daemon whenever it is called,
        and redirect the output to a file
        Arguments: None
        Returns  : Object of Bluetooth-d Daemon process.
        """
        cmd = "/usr/local/bluez/bluez-tools/libexec/bluetooth/bluetoothd -ndE"
        file_handler_btd = open("bluetoothd.log", 'a+')
        self.__Process2 = subprocess.Popen(cmd, shell=True, stdout=file_handler_btd, stderr=file_handler_btd)
        if self.__Process2.returncode == None:
            log.info(" Bluetooth-d Daemon Initiated....")
            log.info("*"*100)
        else:
            log.info(" Failed to init "'Bluetooth-d Daemon'" ")
            sys.exit(1)
        return self.__Process2
    def pulseaudio(self):
        """
        This method will run the `Pulseaudio` Daemon whenever it is called,
        and re-direct the output to a file.
        Arguments: None
        Returns  : Object of Pulseaudio Daemon Process.
        """
        cmd = "/usr/local/bluez/pulseaudio-13.0_for_bluez-5.54/bin/pulseaudio -vvv"
        file_handler_pulse = open("Pulseaudio.log", 'a+')
        self.__Process3 = subprocess.Popen(cmd, shell=True, stdout=file_handler_pulse, stderr=file_handler_pulse)
        Process3 = subprocess.Popen(cmd, shell=True, stdout=file_handler_pulse, stderr=file_handler_pulse)
        if Process3.returncode == None:
            pass
        if self.__Process3.returncode == None:
            log.info(" Pulseaudio Daemon Initiated....")
        else:
            log.info(" Failed to init "'Pulseaudio Daemon'" ")
            sys.exit(1)
        return self.__Process3

def convert_colon_underscore_with_path(*args):
    """
        This Function is to convert the ":" in BD_ADDRESS to "_" with object path
        Arguments:-
                    BD_ADDRESS
                    Adapter_interfcae: eg:- either "hci0" or "hci1"
        Returns:-
                    Object path
    """
    bus = dbus.SystemBus()
    device = args[0]
    adapter_port = args[1]

    lst = list(device)
    leng = len(lst)
    for i in range(leng):
        if lst[i] == ':': 
                lst[i] = '_'

    lst = "".join(lst)
    new_bd_address = str(lst)
    my_adapter = adapter_port + "/dev_"
    my_device = my_adapter + new_bd_address
    return my_device 

def check_active_dongles():
    """
        This Function is to Check the Active Dongles Connected to the USB-Ports
        Arguments:-
                    None
        Returns:-
                Selected Dongle opted by user.
    """
    bus = dbus.SystemBus()
    list_of_active_dongle = []
    try:
        manager = dbus.Interface(bus.get_object(gl.SERVICE_NAME, gl.ROOT), gl.D_BUS_OBJECT_MANAGER)
        objects = manager.GetManagedObjects()
    except Exception as e:
        log.critical(e)

    for path, interface in objects.items():

        if len(path) == 15:
            list_of_active_dongle.append(path)

    log.info("======= List of Active Dongles ========")
    temp_variable = 1
    check = len(list_of_active_dongle)
    if check == 0:
        # if it is zero then no dongles are connected
        error = 0
        return error
        sys.exit(1)

    for i in list_of_active_dongle:
        #log.info(str(temp_variable), str(i))
        log.info("{}: {}".format(str(temp_variable),str(i)))
        temp_variable = temp_variable + 1

    dongle_choise = int(raw_input(" Choose your Dongle interface out of listed data ......"))
    length_of_list = len(list_of_active_dongle)
    if dongle_choise > length_of_list:
        log.info(" Invalid choise!")
        sys.exit(1)

    ADAPTER_OBJ = list_of_active_dongle[dongle_choise - 1]

    return str(ADAPTER_OBJ)

def check_paired_device():
    """
         This Function is to Check the paired devices .
         Arguments:-
                    None
         Returns:-
                    list of paired devices
    """
    bus = dbus.SystemBus()
    list_of_pair_device = []
    try:
        manager = dbus.Interface(bus.get_object(gl.SERVICE_NAME,gl.ROOT),gl.D_BUS_OBJECT_MANAGER)
        objects = manager.GetManagedObjects()
    except Exception as e:
        log.critical(e)

    for path, interface in objects.items():
        if len(path) > 16 and len(path) <= 38:
            try:
                proxy_obj = bus.get_object(gl.SERVICE_NAME, path)
                adapter_interface = dbus.Interface(proxy_obj, gl.D_BUS_PROPERTIES)
            except Exception as e:
                log.critical(e)
            try:
                ret = adapter_interface.Get(gl.DEVICE_INTERFACE, "Paired")
            except Exception as e:
                log.critical(e)

            if ret == 1:
                address = adapter_interface.Get(gl.DEVICE_INTERFACE, "Address")
                count = 0
                for index in list_of_pair_device:
                    if index == address:
                        count = 1
                if count == 0:
                    list_of_pair_device.append(address)

    return list_of_pair_device

def add_uuid_with_names(UUID):
    """
        This Function is to Address the UUID's with there respective names.
        Arguments:-
                    Array of UUID's
        Returns:-
                    Dictionary
                    key: names
                    value: UUID
    """
    dummy_dict = {}
    for i in UUID:

        if i == "0000110a-0000-1000-8000-00805f9b34fb":
            dummy_dict["Audio Source"] = i

        elif i == "0000110c-0000-1000-8000-00805f9b34fb":
            dummy_dict["A/V Remote Control Target"] = i

        elif i == "0000110e-0000-1000-8000-00805f9b34fb":
            dummy_dict["A/V Remote Control"] = i

        elif i == "00001112-0000-1000-8000-00805f9b34fb":
            dummy_dict["Headset AG"] = i

        elif i == "00001200-0000-1000-8000-00805f9b34fb":
            dummy_dict["PnP Information"] = i

        elif i == "00001800-0000-1000-8000-00805f9b34fb":
            dummy_dict["Generic Access Profile"] = i

        elif i == "00001801-0000-1000-8000-00805f9b34fb":
            dummy_dict["Generic Attribute Profile"] = i

        elif i == "00001105-0000-1000-8000-00805f9b34fb":
            dummy_dict["OBEXObjectPush"] = i

        elif i == "0000111f-0000-1000-8000-00805f9b34fb":
            dummy_dict["HandsfreeAudioGateway"] = i

        elif i == "0000110d-0000-1000-8000-00805f9b34fb":
            dummy_dict["AdvanceAudioDistribution"] = i

        elif i == "00001106-0000-1000-8000-00805f9b34fb":
            dummy_dict["OBEX File Transfer"] = i

        elif i == "0000112f-0000-1000-8000-00805f9b34fb":
            dummy_dict["Phonebook Access Server"] = i

        elif i == "00001132-0000-1000-8000-00805f9b34fb":
            dummy_dict["Message Access Server"] = i

        elif i == "00001108-0000-1000-8000-00805f9b34fb":
            dummy_dict["Headset"] = i

    return dummy_dict









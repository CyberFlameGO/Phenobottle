import serial
import glob
import sys
import time
from phenobottle import config


def list_serial_ports():
    """
    Function works with MacOS, Windows and Linux OS
    @returns an array of serial ports
    """
    # Windows
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    # Linux
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    # MacOS
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError("Unsupported platform")

    portsList = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            if("Bluetooth" not in port):  # Excludes bluetooth port on Mac OS
                portsList.append(port)
        except (OSError, serial.SerialException):
            pass
    if(len(portsList) == 0):
        raise IndexError("No USB devices found. Ensure your machine is connected to a Phenobottles microcontroller.")
    else:
        return portsList 


def connect(portsList=None):
    """
    Connects to a serial port using the DEFAULT serial port (found in config.yaml) then tries the ports list.

    TODO: Need to handle multiple ports cleanly.
    @returns a serial device or False if a connection cannot be made
    """
    settings = config.get_configuration()
    device = serial.Serial(settings["serial"]["port"])
    if(device.is_open):
        print("Connected to the default serial device: {} and configured sucessfully.".format(settings["serial"]["port"]))
        return device
    elif(len(portsList) == 1):
        device = serial.Serial(portsList[0])
        if(device.is_open):
            print("Connected to serial device: {} and configured sucessfully.".format(portsList[0]))
            return device
        else:
            print("Single serial device found: {} however a connection request was unsuccessful.".format(portsList[0]))
    else:
        print("Multiple serial devices found. Configure the port you wish to connect to in the config.yaml file.")
    return False 


def disconnect(device):
    """
    Disconnect from serial device.
    @returns True if sucessful False if not
    """
    device.close()
    if(device.is_open):
        print("Unable to close serial device: {}".format(device))
        return False
    else:
        print("Disconnected from serial device cleanly.")
        return True


def send_command(command, device=None, response=False, timeout=5):
    # Open connection if not already open
    if not device:
        device = connect()
    # Clear serial port
    device.flush() 
    try:
        print("Sending command: " + command.decode("utf-8"))
    except AttributeError as err:
        print("Sending command: " + command)
    device.write(command)
    if response:
        for _ in range(timeout):
            res = str(device.readline()[:-2], 'utf-8') # Remove \r\n and decode
            if res != None:
                print("Recieved response: " + res)
                return res
            time.sleep(1) 


if __name__ == "__main__":
    portsList = list_serial_ports()
    mc = connect(portsList)
    print(send_command(mc, "T", True))
    disconnect(mc)

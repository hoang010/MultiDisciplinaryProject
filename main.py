# Import written classes
from RPi.PC import PC
from RPi.Tablet import Tablet
from RPi.Arduino import Arduino
from config.text_color import TextColor as text_color

# Import libraries
import threading
import socket
import serial
import time


def main(sys_type):

    # Initialise required stuff here
    pc_ip = ''
    rpi_ip = '192.168.17.17'
    port = '80'
    host_mac_addr = ''
    arduino_name = ''

    # If running on Pi, run relevant threads
    if sys_type == 'Linux':
        rpi(pc_ip, port, host_mac_addr, arduino_name)

    # If running on own PC, run instance of algorithms
    elif sys_type == 'Windows' or sys_type == 'Darwin':
        pc(rpi_ip, port)


def rpi(pc_ip, port, host_mac_addr, arduino_name):
    
    # Connect to Arduino
    arduino_object = Arduino(arduino_name, text_color)

    # Connect to PC
    pc_object = PC(pc_ip, port, text_color)
    pc_connection = threading.Thread(target=pc_object.connect())

    # Connect to Tablet
    tablet_object = Tablet(host_mac_addr, text_color)
    tablet_connection = threading.Thread(target=tablet_object.connect())

    print(text_color.BOLD +
          'PC socket running on thread 1.'
          + text_color.ENDC)
    pc_connection.start()

    print(text_color.BOLD +
          'Tablet socket running on thread 2.'
          + text_color.ENDC)
    tablet_connection.start()

    return


def pc(rpi_ip, port):
    s = socket.socket()

    try:
        print(text_color.BOLD +
              'Connecting to ' + rpi_ip + ':' + port
              + text_color.ENDC)

        s.connect((rpi_ip, port))

        print(text_color.OKGREEN +
              'Connected to ' + rpi_ip + ':' + port
              + text_color.ENDC)

    except:
        print(text_color.FAIL +
              'Connection failed/terminated'
              + text_color.ENDC)


if __name__ == "__main__":
    import platform
    main(platform.system())

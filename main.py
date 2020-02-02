# Import written classes
from RPi.PC import PC
from RPi.Tablet import Tablet
from RPi.Arduino import Arduino
from RPi.Camera import Camera
from config.text_color import TextColor as text_color

# Import libraries
import queue
import socket
import time


def main(sys_type):

    # Initialise required stuff here
    rpi_ip = '192.168.17.17'
    port = '80'
    rpi_mac_addr = ''
    arduino_name = ''

    # If running on Pi, run relevant threads
    if sys_type == 'Linux':
        rpi(rpi_ip, port, rpi_mac_addr, arduino_name)

    # If running on own PC, run instance of algorithms
    elif sys_type == 'Windows' or sys_type == 'Darwin':
        pc(rpi_ip, port)


def rpi(rpi_ip, port, rpi_mac_addr, arduino_name):
    
    # Connect to Arduino
    arduino_object = Arduino(arduino_name, text_color)

    # Connect to PC
    pc_object = PC(rpi_ip, port, text_color)
    pc_socket, pc_addr = pc_object.connect()

    # Connect to Tablet
    tablet_object = Tablet(rpi_mac_addr, text_color)
    tablet_socket, tablet_info = tablet_object.connect()

    while True:

        # Receive data from tablet
        mode = tablet_object.receive_data(tablet_socket)

        # If no data received, wait for tablet to send data
        while not mode:
            mode = tablet_object.receive_data(tablet_socket)

        # Send acknowledgment once data from tablet is received
        tablet_object.send_data(tablet_socket, tablet_info, '{} acknowledged'.format(mode))

        # 4 modes to accommodate for: Explore, Image Recognition, Shortest Path and Manual
        if mode == 'Explore':

        elif mode == 'Image Recognition':

        elif mode == 'Shortest Path':

        elif mode == 'Manual':


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

# Import written classes
from RPi.PC import PC
from RPi.Tablet import Tablet
from RPi.Arduino import Arduino
# from RPi.Camera import Camera
# from Algo.explore import Explore
# from Algo.image_recognition import ImageRecognition
# from Algo.shortest_path import ShortestPath
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

    print(text_color.WARNING + 'End of program reached.' + text_color.ENDC)


def rpi(rpi_ip, port, rpi_mac_addr, arduino_name):
    
    # Connect to Arduino
    arduino_object = Arduino(arduino_name, text_color)

    # Connect to PC
    pc_object = PC(rpi_ip, port, text_color)
    pc_socket, pc_addr = pc_object.connect()

    # Connect to Tablet
    tablet_object = Tablet(rpi_mac_addr, text_color)
    tablet_socket, tablet_info = tablet_object.connect()

    # Receive data from tablet
    mode = tablet_object.receive_data(tablet_socket)

    # 4 modes to accommodate for: Explore, Image Recognition, Shortest Path, Manual and Disconnect
    if mode in ['Explore', 'Image Recognition', 'Shortest Path', 'Manual', 'Disconnect']:
        tablet_object.send_data(tablet_socket, tablet_info, '{} acknowledged'.format(mode))
        print(text_color.OKGREEN + '{} Mode Initiated'.format(mode) + text_color.ENDC)

        if mode == 'Explore':
            print(mode)

        elif mode == 'Image Recognition':
            print(mode)

        elif mode == 'Shortest Path':
            print(mode)

        elif mode == 'Manual':
            print(mode)

        elif mode == 'Disconnect':
            pc_object.disconnect(pc_socket, pc_addr)
            tablet_object.disconnect(tablet_socket, tablet_info)
            return

    else:
        print(text_color.FAIL + 'Invalid argument received.' + text_color.ENDC)
        tablet_object.send_data(tablet_socket, tablet_info, 'Send valid argument')


def pc(rpi_ip, port):
    sock = socket.socket()

    try:
        print(text_color.BOLD +
              'Connecting to ' + rpi_ip + ':' + port
              + text_color.ENDC)

        sock.connect((rpi_ip, port))

        print(text_color.OKGREEN +
              'Connected to ' + rpi_ip + ':' + port
              + text_color.ENDC)

    except:
        raise Exception("Connection to {}:{} failed".format(rpi_ip, port))

    data = sock.recv(bufsize=1)

    # 4 modes to accommodate for: Explore, Image Recognition, Shortest Path, Manual and Disconnect
    sock.sendmsg('{} acknowledged'.format(data))
    print(text_color.OKGREEN + '{} Mode Initiated'.format(data) + text_color.ENDC)

    if data == 'Explore':
        print(data)

    elif data == 'Image Recognition':
        print(data)

    elif data == 'Shortest Path':
        print(data)

    elif data == 'Manual':
        print(data)

    elif data == 'Disconnect':
        sock.close()
        print(text_color.OKGREEN +
              'Connection to {}:{} closed'.format(rpi_ip, port)
              + text_color.ENDC)
        return

    # else:
    #     print(text_color.FAIL + 'Invalid argument received.' + text_color.ENDC)
    #     sock.sendmsg('Send valid argument')


if __name__ == "__main__":
    import platform
    main(platform.system())

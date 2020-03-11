# Import written classes
from RPi.server import Server
from RPi.bluetooth import Bluetooth
from RPi.arduino import Arduino
from RPi.client import Client
from config.text_color import TextColor as text_color

# Import libraries
import time
import cv2
import os


def main(sys_type):
    # Initialise required stuff here
    rpi_ip = '192.168.17.17'
    rpi_mac_addr = 'B8:27:EB:52:AC:83'
    # USB port name!!
    arduino_name = ''

    log_string = text_color.OKBLUE + "{} | Main: ".format(time.asctime()) + text_color.ENDC
    # If running on Pi, run relevant threads
    if sys_type == 'Linux':
        rpi(rpi_ip, rpi_mac_addr, arduino_name, log_string)

    # If running on own PC, run instance of algorithms
    elif sys_type == 'Windows' or sys_type == 'Darwin':
        pc(rpi_ip, log_string)

    print(text_color.WARNING + 'End of program reached.' + text_color.ENDC)


def rpi(rpi_ip, rpi_mac_addr, arduino_name, log_string):
    """
    Function to start running code on Raspberry Pi
    :param rpi_ip: String
            String containing IP address of Raspberry Pi
    :param rpi_mac_addr: String
            String containing MAC address of Raspberry Pi
    :param arduino_name: String
            String containing Arduino device name
    :param log_string: String
            String containing format of log to be used
    :return:
    """
    try:
        while True:

            # Menu
            print('1. Connect to Arduino')
            print('2. Connect via Bluetooth')
            print('3. Connect to PC')
            print('4. Test Arduino')
            print('5. Test Bluetooth message')
            print('6. Test PC message')
            print('7. Disconnect Arduino')
            print('8. Disconnect Bluetooth')
            print('9. Disconnect PC')
            print('10. Disconnect all')

            # Prompt for input
            choice = int(input('Choose an option: '))

            # If sending string, get string from user
            if 3 < choice < 7:
                message = input('Enter string: ')

            if choice == 1:
                # Connect to Arduino
                arduino_conn_test = Arduino(arduino_name, text_color)

            elif choice == 2:
                # Initialise class
                bt_conn_test = Bluetooth(rpi_mac_addr, text_color)

                # Listen for device
                bt_conn_test.listen()

            elif choice == 3:
                # Initialise class
                server_test = Server(rpi_ip, 7777, text_color)

                # Listen for requests for connection
                server_test.listen()

            elif choice == 4:

                # Send message to Arduino after encoding it in bytes
                arduino_conn_test.send(message.encode())

                # Display sent message
                print(log_string + text_color.BOLD + '"{}" sent'.format(message) + text_color.ENDC)

                # Wait for received message
                recv_string = arduino_conn_test.recv()

                # Decode received message (that is in bytes)
                recv_string = recv_string.decode()

                # Display received message
                print(log_string + text_color.BOLD + '"{}" received'.format(recv_string) + text_color.ENDC)

            elif choice == 5:
                # Send message to Tablet after encoding it in bytes
                bt_conn_test.send(message.encode())

                # Display sent message
                print(log_string + text_color.BOLD + '"{}" sent'.format(message) + text_color.ENDC)

                # Wait for received message
                recv_string = bt_conn_test.recv()

                # Decode received message (that is in bytes)
                recv_string = recv_string.decode()

                # Display received message
                print(log_string + text_color.BOLD + '"{}" received'.format(recv_string) + text_color.ENDC)

            elif choice == 6:
                # Send message to PC after encoding it in bytes
                server_test.send(message.encode())

                # Display sent message
                print(log_string + text_color.BOLD + '"{}" sent'.format(message) + text_color.ENDC)

                # Wait for received message
                recv_string = server_test.recv()

                # Decode received message (that is in bytes)
                recv_string = recv_string.decode()

                # Display received message
                print(log_string + text_color.BOLD + '"{}" received'.format(recv_string) + text_color.ENDC)

            elif choice == 7:
                # Disconnect from Arduino only
                arduino_conn_test.disconnect()
                print(log_string + text_color.BOLD + 'Arduino disconnected' + text_color.ENDC)

            elif choice == 8:
                # Disconnect from Tablet only
                bt_conn_test.disconnect()
                print(log_string + text_color.BOLD + 'Bluetooth disconnected' + text_color.ENDC)

            elif choice == 9:
                # Disconnect from PC only
                server_test.disconnect()
                print(log_string + text_color.BOLD + 'Server send disconnected' + text_color.ENDC)

            elif choice == 10:
                # Disconnect from all
                server_test.disconnect()
                print(log_string + text_color.BOLD + 'Server send disconnected' + text_color.ENDC)

                bt_conn_test.disconnect()
                print(log_string + text_color.BOLD + 'Bluetooth disconnected' + text_color.ENDC)

                arduino_conn_test.disconnect()
                print(log_string + text_color.BOLD + 'Arduino disconnected' + text_color.ENDC)

            else:
                # Display invalid choice number
                print(log_string + text_color.FAIL + 'Invalid choice number {}'.format(choice) + text_color.ENDC)

    except KeyboardInterrupt:
        os.system('pkill -9 python')


def pc(rpi_ip, log_string):
    """
    Function to start running code on PC
    :param rpi_ip: String
            String containing IP address of Raspberry Pi
    :param log_string: String
            String containing format of log to be used
    :return:
    """
    # Create an instance of PC
    pc_test = Client(rpi_ip, 7777, text_color)

    # Connect to Raspberry Pi
    pc_test.connect()

    try:
        while True:

            # Receive data from RPi
            msg = pc_test.recv()

            # Decode data (that is in bytes)
            msg = msg.decode()

            # Display message
            print(log_string + text_color.BOLD + '{} received'.format(msg) + text_color.ENDC)

            if msg == 'disconnect':
                pc_test.disconnect()
                print(log_string + text_color.BOLD + 'Client recv diconnected' + text_color.ENDC)

            else:
                pc_test.send(('"{}" returned!'.format(msg)).encode())

    except KeyboardInterrupt:
        os.system('pkill -9 python')


if __name__ == "__main__":
    import platform
    try:
        main(platform.system())
        # main('Windows')
    except KeyboardInterrupt:
        os.system('pkill -9 python')

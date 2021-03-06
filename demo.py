# Import written classes
from RPi.server import Server
from RPi.bluetooth import Bluetooth
from RPi.arduino import Arduino
from RPi.client import Client
from Algo.explore import Explore
# from Algo.image_recognition import ImageRecognition
# from Algo.shortest_path import ShortestPath
from config.text_color import TextColor as text_color
from config.direction import Direction

# Import libraries
import time
import cv2
import os
import json


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

    # Connect to Arduino
    arduino_conn_demo = Arduino(arduino_name, text_color)
    arduino_conn_demo.recv()

    # Connect to PC
    server_conn = Server(rpi_ip, 7777, text_color)
    server_conn.listen()

    # Connect to Tablet
    bt_conn_demo = Bluetooth(rpi_mac_addr, text_color)
    bt_conn_demo.listen()

    try:
        while True:

            print(text_color.WARNING + "This is a demonstration" + text_color.ENDC)
            print('1. Information passing')
            print('2. Straight line motion')
            print('3. Rotation')
            print('4. Obstacle avoidance and position recovery')
            print('5. Extension: Obstacle avoidance with diagonal movement')
            print('6. Disconnect all')
            choice = int(input('Choose an option: '))

            # Pass info
            if choice == 1:

                print(log_string + text_color.OKGREEN + 'Info passing' + text_color.ENDC)

                bt_conn_demo.send('Get info'.encode())

                # Receive info from tablet
                info = bt_conn_demo.recv()

                # Send info to Arduino
                arduino_conn_demo.send(info.encode())

                # Sleep for 5s while Arduino increments data and sends it back
                time.sleep(5)

                # Receive updated info from Arduino
                new_info = arduino_conn_demo.recv()

                # Send to PC
                server_conn.send(new_info.encode())

            # Straight line motion
            elif choice == 2:

                print(log_string + text_color.OKGREEN + 'Straight line motion' + text_color.ENDC)

                arduino_conn_demo.send('3'.encode())

                dist = int(input('Enter number of grids to move: '))
                i = 1

                while dist > 0:
                    arduino_conn_demo.send(b'3')

                    arduino_conn_demo.send()

                    print(log_string + text_color.OKGREEN + 'Moved by {} grid'.format(i) + text_color.ENDC)

                    i += 1
                    dist -= 1

            # Rotation
            elif choice == 3:

                for i in range(2):
                    print(log_string + text_color.OKGREEN + 'Turning left by 180 degrees' + text_color.ENDC)
                    arduino_conn_demo.send(b'7')

                    arduino_conn_demo.recv()

                    print(log_string + text_color.OKGREEN + 'Done!' + text_color.ENDC)

                for i in range(2):
                    print(log_string + text_color.OKGREEN + 'Turning right by 180 degrees' + text_color.ENDC)
                    arduino_conn_demo.to_send_queue.put(b'8')

                    arduino_conn_demo.send()

                    print(log_string + text_color.OKGREEN + 'Done!' + text_color.ENDC)

            # Obstacle avoidance and position recovery
            elif choice == 4:

                # Declare variables here
                total_dist = 15
                i = 1

                print(log_string + text_color.OKGREEN + 'Obstacle avoidance and position recovery' + text_color.ENDC)
                arduino_conn_demo.send(b'2')

                obs_dist = arduino_conn_demo.recv()

                obs_dist = json.loads(obs_dist)

                obs_dist = int(obs_dist["TopMiddle"]) / 10

                print(log_string + text_color.OKGREEN + 'Obstacle at distance: {}'.format(obs_dist) + text_color.ENDC)

                obs_dist = (int(obs_dist) / 10) - 1

                while obs_dist > 0:
                    arduino_conn_demo.send(b'3')

                    arduino_conn_demo.recv()

                    print(log_string + text_color.OKGREEN + 'Moved by {}'.format(i) + text_color.ENDC)

                    i += 1
                    obs_dist -= 1

                arduino_conn_demo.send(b'2')

                check_left_obs = arduino_conn_demo.recv()

                check_left_obs = json.loads(check_left_obs)

                check_left_obs = int(check_left_obs["LeftSide"]) / 10

                if not check_left_obs:
                    action_order = [b'4', b'3', b'5', b'3', b'3', b'5', b'3', b'4']

                else:
                    action_order = [b'5', b'3', b'4', b'3', b'3', b'4', b'3', b'5']

                # Declare variables here again
                remain_dist = total_dist - obs_dist
                i = 0

                for num in action_order:
                    arduino_conn_demo.send(num)

                    arduino_conn_demo.recv()

                while remain_dist > 0:
                    arduino_conn_demo.send(b'3')

                    arduino_conn_demo.recv()

                    print(log_string + text_color.OKGREEN + 'Moved by {}'.format(i) + text_color.ENDC)

                    i += 1
                    remain_dist -= 1

            # Extension: Obstacle avoidance with diagonal movement
            elif choice == 5:
                # TODO: Check if Arduino is able to move diagonally
                pass

            elif choice == 6:
                server_conn.disconnect()
                print(log_string + text_color.BOLD + 'Server disconnected' + text_color.ENDC)

                bt_conn_demo.disconnect()
                print(log_string + text_color.BOLD + 'Bluetooth disconnected' + text_color.ENDC)

                arduino_conn_demo.disconnect()
                print(log_string + text_color.BOLD + 'Arduino disconnected' + text_color.ENDC)


            else:
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
    pc_conn = Client(rpi_ip, 7777, text_color)

    # Connect to Raspberry Pi
    pc_conn.connect()

    try:
        while True:

            # TODO: Array here!
            msg = pc_conn.recv()

            msg = msg.decode()

            msg = str(chr(int(msg)))

            print(log_string + text_color.BOLD + '{} received'.format(msg) + text_color.ENDC)

            if msg == 'disconnect':
                pc_conn.disconnect()
                print(log_string + text_color.BOLD + 'Client diconnected' + text_color.ENDC)

            else:
                pc_conn.send(('"{}" returned!'.format(msg)).encode())

    except KeyboardInterrupt:
        os.system('pkill -9 python')


if __name__ == "__main__":
    import platform
    try:
        # main(platform.system())
        main('Windows')
    except KeyboardInterrupt:
        os.system('pkill -9 python')

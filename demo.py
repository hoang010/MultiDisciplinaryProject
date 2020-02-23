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

    # Connect to PC
    server_send_demo = Server('server_send_demo', 'send', rpi_ip, 7777, text_color)
    server_recv_demo = Server('server_recv_demo', 'recv', rpi_ip, 8888, text_color)
    server_stream_demo = Server('server_stream_demo', 'send', rpi_ip, 9999, text_color)
    server_send_demo.listen()
    server_recv_demo.listen()
    server_stream_demo.listen()

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

                bt_conn_demo.to_send_queue.put('Get info'.encode())

                # Receive info from tablet
                info = bt_conn_demo.have_recv_queue.get()

                # Send info to Arduino
                arduino_conn_demo.to_send_queue.put(info.encode())

                # Sleep for 5s while Arduino increments data and sends it back
                time.sleep(5)

                # Receive updated info from Arduino
                new_info = arduino_conn_demo.have_recv_queue.get()

                # Send to PC
                server_send_demo.queue.put(new_info.encode())

            # Straight line motion
            elif choice == 2:

                print(log_string + text_color.OKGREEN + 'Straight line motion' + text_color.ENDC)
                arduino_conn_demo.to_send_queue.put('2'.encode())

                dist = get_sensor_data(arduino_conn_demo)
                print(log_string + text_color.OKGREEN + 'Distance to move: {} cm'.format(dist) + text_color.ENDC)

                dist = int(dist)/10
                i = 1

                while dist > 0:
                    arduino_conn_demo.to_send_queue.put('3'.encode())

                    get_sensor_data(arduino_conn_demo)

                    print(log_string + text_color.OKGREEN + 'Moved by {} grid'.format(i) + text_color.ENDC)

                    i += 1
                    dist -= 1

            # Rotation
            elif choice == 3:

                for i in range(2):
                    print(log_string + text_color.OKGREEN + 'Turning left by 180 degrees' + text_color.ENDC)
                    arduino_conn_demo.to_send_queue.put('7'.encode())

                    get_sensor_data(arduino_conn_demo)

                    print(log_string + text_color.OKGREEN + 'Done!' + text_color.ENDC)

                for i in range(2):
                    print(log_string + text_color.OKGREEN + 'Turning right by 180 degrees' + text_color.ENDC)
                    arduino_conn_demo.to_send_queue.put('8'.encode())

                    get_sensor_data(arduino_conn_demo)

                    print(log_string + text_color.OKGREEN + 'Done!' + text_color.ENDC)

            # Obstacle avoidance and position recovery
            elif choice == 4:

                # Declare variables here
                total_dist = 15
                i = 1

                print(log_string + text_color.OKGREEN + 'Obstacle avoidance and position recovery' + text_color.ENDC)
                arduino_conn_demo.to_send_queue.put('2'.encode())

                obs_dist = get_sensor_data(arduino_conn_demo)

                print(log_string + text_color.OKGREEN + 'Obstacle at distance: {}'.format(obs_dist) + text_color.ENDC)

                obs_dist = (int(obs_dist) / 10) - 1

                while obs_dist > 0:
                    arduino_conn_demo.to_send_queue.put('3'.encode())

                    get_sensor_data(arduino_conn_demo)

                    print(log_string + text_color.OKGREEN + 'Moved by {}'.format(i) + text_color.ENDC)

                    i += 1
                    obs_dist -= 1

                check_left_obs = get_sensor_data(arduino_conn_demo)

                if not check_left_obs:
                    action_order = ['4', '3', '5', '3', '3', '5', '3', '4']

                else:
                    action_order = ['5', '3', '4', '3', '3', '4', '3', '5']

                # Declare variables here again
                remain_dist = total_dist - obs_dist
                i = 0

                for num in action_order:
                    arduino_conn_demo.to_send_queue.put(num.encode())

                    get_sensor_data(arduino_conn_demo)

                while remain_dist > 0:
                    arduino_conn_demo.to_send_queue.put('3'.encode())

                    get_sensor_data(arduino_conn_demo)

                    print(log_string + text_color.OKGREEN + 'Moved by {}'.format(i) + text_color.ENDC)

                    i += 1
                    remain_dist -= 1

            # Extension: Obstacle avoidance with diagonal movement
            elif choice == 5:
                # TODO: Check if Arduino is able to move diagonally
                pass

            elif choice == 6:
                server_send_demo.disconnect()
                print(log_string + text_color.BOLD + 'Server send disconnected' + text_color.ENDC)
                server_recv_demo.disconnect()
                print(log_string + text_color.BOLD + 'Server recv disconnected' + text_color.ENDC)
                server_stream_demo.disconnect()
                print(log_string + text_color.BOLD + 'Server stream disconnected' + text_color.ENDC)

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
    pc_send_test = Client('pc_send_test', 'send', rpi_ip, 7777, text_color)
    pc_recv_test = Client('pc_recv_test', 'recv', rpi_ip, 8888, text_color)
    pc_stream_test = Client('pc_stream_test', 'recv', rpi_ip, 9999, text_color)

    # Connect to Raspberry Pi
    pc_send_test.connect()
    pc_recv_test.connect()
    pc_stream_test.connect()

    try:
        while True:

            # TODO: Array here!
            msg = pc_recv_test.queue.get()

            msg = msg.decode()

            print(log_string + text_color.BOLD + '{} received'.format(msg) + text_color.ENDC)

            if msg == 'stream':
                while True:

                    # Receive stream from socket
                    stream = pc_stream_test.queue.get()

                    stream = stream.decode()

                    # Display stream in a window
                    cv2.imshow('Stream from Pi', stream)

                    # If end of stream (indicated with return value 0), break
                    if not stream:
                        break

            elif msg == 'disconnect':
                pc_send_test.disconnect()
                print(log_string + text_color.BOLD + 'Client send diconnected' + text_color.ENDC)

                pc_recv_test.disconnect()
                print(log_string + text_color.BOLD + 'Client recv disconnected' + text_color.ENDC)

                pc_stream_test.disconnect()
                print(log_string + text_color.BOLD + 'Client stream disconnected' + text_color.ENDC)

            else:
                pc_send_test.queue.put(('"{}" returned!'.format(msg)).encode())

    except KeyboardInterrupt:
        os.system('pkill -9 python')


def get_sensor_data(arduino_conn_demo):
    """
    Function to get sensor data
    :param arduino_conn_demo: Serial
            Serial port containing connection to Arduino
    :return: Array
            Array containing sensor data
    """
    data = arduino_conn_demo.have_recv_queue.get()

    data = data.decode()

    return data


if __name__ == "__main__":
    import platform
    try:
        main(platform.system())
        # main('Windows')
    except KeyboardInterrupt:
        os.system('pkill -9 python')

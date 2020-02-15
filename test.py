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

    while True:

        print('1. Connect to Arduino')
        print('2. Connect via Bluetooth')
        print('3. Connect to PC')
        print('4. Test Arduino')
        print('5. Test Bluetooth message')
        print('6. Test PC message')
        print('7. Test PC stream')
        print('8. Disconnect Arduino')
        print('9. Disconnect Bluetooth')
        print('10. Disconnect PC')
        print('11. Disconnect all')
        choice = int(input('Choose an option: '))

        if 3 < choice < 7:
            message = input('Enter string: ')

        if choice == 1:
            # Connect to Arduino
            arduino_conn_test = Arduino(arduino_name, text_color)

        elif choice == 2:
            # Connect to Tablet
            bt_conn_test = Bluetooth(rpi_mac_addr, text_color)
            bt_conn_test.listen()

        elif choice == 3:
            # Connect to PC
            server_send_test = Server('server_send_test', 'send', rpi_ip, 7777, text_color)
            server_recv_test = Server('server_recv_test', 'recv', rpi_ip, 8888, text_color)
            server_stream_test = Server('server_stream_test', 'send', rpi_ip, 9999, text_color)
            server_send_test.listen()
            server_recv_test.listen()
            server_stream_test.listen()

        elif choice == 4:
            arduino_conn_test.to_send_queue.put(message.encode())
            recv_string = arduino_conn_test.have_recv_queue.get()

            while not recv_string:
                recv_string = arduino_conn_test.have_recv_queue.get()

            recv_string = recv_string.decode()

            print(log_string + text_color.BOLD + '"{}" received'.format(recv_string) + text_color.ENDC)

        elif choice == 5:
            # TODO: RPi message to Tablet here!
            bt_conn_test.to_send_queue.put(message.encode())
            recv_string = bt_conn_test.have_recv_queue.get()

            while not recv_string:
                recv_string = bt_conn_test.have_recv_queue.get()

            recv_string = recv_string.decode()

            print(log_string + text_color.BOLD + '"{}" received'.format(recv_string) + text_color.ENDC)

        elif choice == 6:
            # TODO: RPi message to PC here!
            server_send_test.queue.put(message.encode())
            recv_string = server_recv_test.queue.get()

            while not recv_string:
                recv_string = server_recv_test.queue.get()

            recv_string = recv_string.decode()

            print(log_string + text_color.BOLD + '"{}" received'.format(recv_string) + text_color.ENDC)

        elif choice == 7:
            # TODO: RPi array here!
            server_send_test.queue.put('Stream'.encode())
            print(log_string + text_color.BOLD + 'Recorder init' + text_color.ENDC)
            from RPi.recorder import Recorder
            recorder = Recorder()
            print(log_string + text_color.BOLD + 'Recorder start' + text_color.ENDC)
            recorder.start()
            print(log_string + text_color.BOLD + 'Recorder running for 10s' + text_color.ENDC)
            time.sleep(10)
            recorder.stop()
            print(log_string + text_color.BOLD + 'Recorder stop' + text_color.ENDC)


        elif choice == 8:
            arduino_conn_test.disconnect()
            print(log_string + text_color.BOLD + 'Arduino disconnected' + text_color.ENDC)

        elif choice == 9:

            bt_conn_test.disconnect()
            print(log_string + text_color.BOLD + 'Bluetooth disconnected' + text_color.ENDC)

        elif choice == 10:
            server_send_test.disconnect()
            print(log_string + text_color.BOLD + 'Server send disconnected' + text_color.ENDC)
            server_recv_test.disconnect()
            print(log_string + text_color.BOLD + 'Server recv disconnected' + text_color.ENDC)
            server_stream_test.disconnect()
            print(log_string + text_color.BOLD + 'Server stream disconnected' + text_color.ENDC)

        elif choice == 11:
            server_send_test.disconnect()
            print(log_string + text_color.BOLD + 'Server send disconnected' + text_color.ENDC)
            server_recv_test.disconnect()
            print(log_string + text_color.BOLD + 'Server recv disconnected' + text_color.ENDC)
            server_stream_test.disconnect()
            print(log_string + text_color.BOLD + 'Server stream disconnected' + text_color.ENDC)

            bt_conn_test.disconnect()
            print(log_string + text_color.BOLD + 'Bluetooth disconnected' + text_color.ENDC)

            arduino_conn_test.disconnect()
            print(log_string + text_color.BOLD + 'Arduino disconnected' + text_color.ENDC)


        else:
            print(log_string + text_color.FAIL + 'Invalid choice number {}'.format(choice) + text_color.ENDC)


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

    while True:

        # TODO: Array here!
        msg = pc_recv_test.queue.get()

        while not msg:
            msg = pc_recv_test.queue.get()

        msg = msg.decode()

        print(log_string + text_color.BOLD + '{} received'.format(msg) + text_color.ENDC)

        if msg == 'stream':
            while True:

                # Receive stream from socket
                stream = pc_stream_test.queue.get()

                while not stream:
                    stream = pc_stream_test.queue.get()

                stream = stream.decode()

                # Display stream in a window
                cv2.imshow('Stream from Pi', stream)

                # If end of stream (indicated with return value 0), break
                if not stream:
                    break

        if msg == 'disconnect':
            pc_send_test.disconnect()
            print(log_string + text_color.BOLD + 'Client send diconnected' + text_color.ENDC)

            pc_recv_test.disconnect()
            print(log_string + text_color.BOLD + 'Client recv disconnected' + text_color.ENDC)

            pc_stream_test.disconnect()
            print(log_string + text_color.BOLD + 'Client stream disconnected' + text_color.ENDC)

        else:
            pc_send_test.queue.put(('"{}" returned!'.format(msg)).encode())


if __name__ == "__main__":
    import platform
    try:
        main(platform.system())
        # main('Windows')
    except KeyboardInterrupt:
        os.system('pkill -9 python')

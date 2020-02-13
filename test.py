# Import written classes
from RPi.server import Server
from RPi.bluetooth import Bluetooth
from RPi.arduino import Arduino
from RPi.client import Client
from Algo.explore import Explore
from Algo.image_recognition import ImageRecognition
# from Algo.shortest_path import ShortestPath
from config.text_color import TextColor as text_color
from config.direction import Direction

# Import libraries
import time
import cv2


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
    arduino_conn_test = Arduino(arduino_name, text_color)

    # Connect to PC
    server_send_test = Server('server_send_test', 'send', rpi_ip, 7777, text_color)
    server_recv_test = Server('server_recv_test', 'recv', rpi_ip, 8888, text_color)
    server_stream_test = Server('server_stream_test', 'send', rpi_ip, 9999, text_color)
    server_send_test.listen()
    server_recv_test.listen()
    server_stream_test.listen()

    # Connect to Tablet
    bt_conn_test = Bluetooth(rpi_mac_addr, text_color)
    bt_conn_test.listen()

    while True:

        print('1. Test Arduino')
        print('2. Test Bluetooth message')
        print('3. Test PC message')
        print('4. Test PC stream')
        print('5. Quit')
        choice = input('Choose an option: ')

        if choice == 1:
            message = input('Enter string: ')
            arduino_conn_test.to_send_queue.put(message)
            recv_string = arduino_conn_test.have_recv_queue.get()

            while not recv_string:
                recv_string = arduino_conn_test.have_recv_queue.get()

            print(log_string + text_color.BOLD + '"{}" received'.format(recv_string) + text_color.ENDC)

        elif choice == 2:
            message = input('Enter string: ')
            # TODO: RPi message to Tablet here!
            bt_conn_test.to_send_queue.put(message)
            recv_string = bt_conn_test.have_recv_queue.get()

            while not recv_string:
                recv_string = bt_conn_test.have_recv_queue.get()

            print(log_string + text_color.BOLD + '"{}" received'.format(recv_string) + text_color.ENDC)

        elif choice == 3:
            message = input('Enter string: ')
            # TODO: RPi message to PC here!
            server_send_test.queue.put(message)
            recv_string = server_recv_test.queue.get()

            while not recv_string:
                recv_string = server_recv_test.queue.get()

            print(log_string + text_color.BOLD + '"{}" received'.format(recv_string) + text_color.ENDC)

        elif choice == 4:
            # TODO: RPi array here!
            server_send_test.queue.put(['Stream'])
            print(log_string + text_color.BOLD + 'Recorder init' + text_color.ENDC)
            from RPi.recorder import Recorder
            recorder = Recorder()
            print(log_string + text_color.BOLD + 'Recorder start' + text_color.ENDC)
            recorder.start()
            time.sleep(10)
            recorder.stop()
            print(log_string + text_color.BOLD + 'Recorder stop' + text_color.ENDC)

        elif choice == 5:
            print(log_string + text_color.BOLD + 'Server send disconnecting' + text_color.ENDC)
            server_send_test.disconnect()
            print(log_string + text_color.BOLD + 'Server recv disconnecting' + text_color.ENDC)
            server_recv_test.disconnect()
            print(log_string + text_color.BOLD + 'Server stream disconnecting' + text_color.ENDC)
            server_stream_test.disconnect()

            print(log_string + text_color.BOLD + 'Bluetooth disconnecting' + text_color.ENDC)
            bt_conn_test.disconnect()

            print(log_string + text_color.BOLD + 'Arduino disconnecting' + text_color.ENDC)
            arduino_conn_test.disconnect()

    # while True:
    #     # Receive data from tablet
    #     # TODO: Bluetooth array here!
    #     mode = bt_conn_test.have_recv_queue.get()[0]
    #
    #     # 4 modes to accommodate for: Explore, Image Recognition, Shortest Path, Manual and Disconnect
    #     if mode in ['Explore', 'Image Recognition', 'Shortest Path', 'Manual', 'Info Passing', 'Disconnect']:
    #
    #         # Send ack to Android device
    #         # TODO: Bluetooth array here!
    #         bt_conn_test.to_send_queue.put(['{} acknowledged'.format(mode)])
    #
    #         # Display on screen the mode getting executed
    #         print(log_string + text_color.OKGREEN + '{} Mode Initiated'.format(mode) + text_color.ENDC)
    #
    #         if mode == 'Explore':
    #             pass
    #
    #         elif mode == 'Image Recognition':
    #             print(mode)
    #
    #         elif mode == 'Shortest Path':
    #             print(mode)
    #
    #         elif mode == 'Manual':
    #             print(mode)
    #
    #         elif mode == 'Info Passing':
    #             pass
    #
    #         elif mode == 'Disconnect':
    #             # Send message to PC and Arduino to tell them to disconnect
    #             # TODO: Rasp Pi array here!
    #             server_send_test.queue.put(['Disconnect'])
    #             arduino_conn_test.to_send_queue.put('Disconnect')
    #
    #             # Wait for 5s to ensure that PC and Arduino receives the message
    #             time.sleep(5)
    #
    #             # Disconnect from wifi and bluetooth connection
    #             server_send_test.disconnect()
    #             server_recv_test.disconnect()
    #             server_stream_test.disconnect()
    #             arduino_conn_test.disconnect()
    #             bt_conn_test.disconnect()
    #             return
    #
    #     else:
    #         # Display feedback so that user knows this condition is triggered
    #         print(log_string + text_color.FAIL +
    #               'Invalid message {} received.'.format(mode)
    #               + text_color.ENDC)
    #
    #         # Add data into queue for sending to tablet
    #         # TODO: Bluetooth array here!
    #         bt_conn_test.to_send_queue.put(['Send valid argument'])


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
        msg = pc_recv_test.queue.get()[0]

        while not msg:
            msg = pc_recv_test.queue.get()[0]

        print(log_string + text_color.BOLD + '{} received' + text_color.ENDC)

        if msg == 'stream':
            while True:

                # Receive stream from socket
                stream = pc_stream_test.queue.get()[0]

                # If end of stream (indicated with return value 0), break
                if not stream:
                    break

                # Display stream in a window
                cv2.imshow('Stream from Pi', stream)

                if not stream:
                    break

        elif msg == 'disconnect':
            print(log_string + text_color.BOLD + 'Client send disconnecting' + text_color.ENDC)
            pc_send_test.disconnect()
            print(log_string + text_color.BOLD + 'Client recv disconnecting' + text_color.ENDC)
            pc_recv_test.disconnect()
            print(log_string + text_color.BOLD + 'Client stream disconnecting' + text_color.ENDC)
            pc_stream_test.disconnect()

        else:
            pc_send_test.queue.put('"{}" returned!'.format(msg))

    # while True:
    #
    #     # Receive data from Raspberry Pi
    #     # TODO: Rasp Pi array here!
    #     data = pc_recv_test.queue.get()[0]
    #
    #     # 4 modes to accommodate for: Explore, Image Recognition, Shortest Path, Manual and Disconnect
    #     if data in ['Explore', 'Image Recognition', 'Shortest Path', 'Manual', 'Info Passing', 'Disconnect']:
    #
    #         # Send ack to Raspberry Pi
    #         # TODO: Rasp Pi array here!
    #         pc_send_test.queue.put(['{} acknowledged'.format(data)])
    #
    #         # Display on screen the mode getting executed
    #         print(log_string + text_color.OKGREEN + '{} mode initiated'.format(data) + text_color.ENDC)
    #
    #         if data == 'Explore':
    #             while True:
    #
    #                 # Receive stream from socket
    #                 stream = pc_stream_test.queue.get()[0]
    #
    #                 # If end of stream (indicated with return value 0), break
    #                 if not stream:
    #                     break
    #
    #                 # Display stream in a window
    #                 cv2.imshow('Stream from Pi', stream)
    #
    #             # TODO: Rasp Pi array here!
    #             real_map_hex = pc_recv_test.queue.get()[0]
    #
    #             print(log_string + text_color.BOLD +
    #                   'Real Map Hexadecimal = {}'.format(real_map_hex)
    #                   + text_color.ENDC)
    #
    #         elif data == 'Image Recognition':
    #             pass
    #
    #         elif data == 'Shortest Path':
    #             print(data)
    #
    #         elif data == 'Manual':
    #             print(data)
    #
    #         elif data == 'Info Passing':
    #             # Wait for 15s
    #             time.sleep(15)
    #
    #             # Get information from pc_recv queue
    #             info = pc_recv_test.queue.get()
    #
    #             # Display info received
    #             print(log_string + text_color.BOLD +
    #                   'Info received = {}'.format(info)
    #                   + text_color.ENDC)
    #
    #         elif data == 'Disconnect':
    #             # Disconnect from Raspberry Pi
    #             pc_send_test.disconnect()
    #             pc_recv_test.disconnect()
    #             pc_stream_test.disconnect()
    #             return
    #
    #     else:
    #
    #         # Display feedback so that user knows this condition is triggered
    #         print(log_string + text_color.FAIL + 'Invalid argument "{}" received.'.format(data) + text_color.ENDC)
    #
    #         # Add data into queue for sending to Raspberry Pi
    #         # Failsafe condition
    #         # TODO: Rasp Pi array here!
    #         pc_send_test.queue.put(['Send valid argument'])


if __name__ == "__main__":
    import platform
    main(platform.system())

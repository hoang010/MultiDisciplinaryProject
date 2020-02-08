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
    arduino_conn = Arduino(arduino_name, text_color)

    # Connect to PC
    server_send = Server('server_send', 'send', rpi_ip, 7777, text_color)
    server_recv = Server('server_recv', 'recv', rpi_ip, 8888, text_color)
    server_stream = Server('server_stream', 'send', rpi_ip, 9999, text_color)
    server_send.listen()
    server_recv.listen()
    server_stream.listen()

    # Connect to Tablet
    bt_conn = Bluetooth(rpi_mac_addr, text_color)
    bt_conn.listen()
    map_size = init(arduino_conn, bt_conn)

    while True:
        # Receive data from tablet
        # TODO: Bluetooth array here!
        mode = bt_conn.have_recv_queue.get()[0]

        # 4 modes to accommodate for: Explore, Image Recognition, Shortest Path, Manual and Disconnect
        if mode in ['Explore', 'Image Recognition', 'Shortest Path', 'Manual', 'Disconnect']:

            # Send ack to Android device
            # TODO: Bluetooth array here!
            bt_conn.to_send_queue.put(['{} acknowledged'.format(mode)])

            # Display on screen the mode getting executed
            print(log_string + text_color.OKGREEN + '{} Mode Initiated'.format(mode) + text_color.ENDC)

            if mode == 'Explore':
                explore(map_size, arduino_conn, bt_conn, server_stream, server_send)

            elif mode == 'Image Recognition':
                print(mode)

            elif mode == 'Shortest Path':
                print(mode)

            elif mode == 'Manual':
                print(mode)

            elif mode == 'Disconnect':
                # Send message to PC and Arduino to tell them to disconnect
                # TODO: Rasp Pi array here!
                server_send.queue.put(['Disconnect'])
                arduino_conn.send('Disconnect')

                # Wait for 5s to ensure that PC and Arduino receives the message
                time.sleep(5)

                # Disconnect from wifi and bluetooth connection
                server_send.disconnect()
                server_recv.disconnect()
                server_stream.disconnect()
                arduino_conn.disconnect()
                bt_conn.disconnect()
                return

        else:
            # Display feedback so that user knows this condition is triggered
            print(log_string + text_color.FAIL +
                  'Invalid message {} received.'.format(mode)
                  + text_color.ENDC)

            # Add data into queue for sending to tablet
            # TODO: Bluetooth array here!
            bt_conn.to_send_queue.put(['Send valid argument'])


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
    pc_send = Client('pc_send', 'send', rpi_ip, 7777, text_color)
    pc_recv = Client('pc_recv', 'recv', rpi_ip, 8888, text_color)
    pc_stream = Client('pc_stream', 'recv', rpi_ip, 9999, text_color)

    # Connect to Raspberry Pi
    pc_send.connect()
    pc_recv.connect()
    pc_stream.connect()

    while True:

        # Receive data from Raspberry Pi
        # TODO: Rasp Pi array here!
        data = pc_recv.queue.get()[0]

        # 4 modes to accommodate for: Explore, Image Recognition, Shortest Path, Manual and Disconnect
        if data in ['Explore', 'Image Recognition', 'Shortest Path', 'Manual', 'Disconnect']:

            # Send ack to Raspberry Pi
            # TODO: Rasp Pi array here!
            pc_send.queue.put(['{} acknowledged'.format(data)])

            # Display on screen the mode getting executed
            print(log_string + text_color.OKGREEN + '{} mode initiated'.format(data) + text_color.ENDC)

            if data == 'Explore':
                while True:

                    # Receive stream from socket
                    stream = pc_stream.queue.get()[0]

                    # If end of stream (indicated with return value 0), break
                    if not stream:
                        break

                    # Display stream in a window
                    cv2.imshow('Stream from Pi', stream)

                # TODO: Rasp Pi array here!
                real_map_hex = pc_recv.queue.get()[0]

                while not real_map_hex:
                    # TODO: Rasp Pi array here!
                    real_map_hex = pc_recv.queue.get()[0]

                print(log_string + text_color.BOLD +
                      'Real Map Hexadecimal = {}'.format(real_map_hex)
                      + text_color.ENDC)

            elif data == 'Image Recognition':
                pass

            elif data == 'Shortest Path':
                print(data)

            elif data == 'Manual':
                print(data)

            elif data == 'Disconnect':
                pc_send.disconnect()
                pc_recv.disconnect()
                pc_stream.disconnect()
                return

        else:

            # Display feedback so that user knows this condition is triggered
            print(log_string + text_color.FAIL + 'Invalid argument "{}" received.'.format(data) + text_color.ENDC)

            # Add data into queue for sending to Raspberry Pi
            # Failsafe condition
            # TODO: Rasp Pi array here!
            pc_send.queue.put(['Send valid argument'])


def explore(map_size, arduino_conn, bt_conn, server_stream, server_send):

    from RPi.recorder import Recorder

    # Start an instance of Recorder class
    recorder = Recorder()

    # Start recording with the Pi camera
    recorder.start()

    # Start an instance of Explore class
    explorer = Explore(map_size, Direction)

    # Start an instance of ImageRecognition class
    img_recognisor = ImageRecognition(text_color)

    # While map is not complete, continue streaming data to PC
    while not explorer.is_map_complete():

        # TODO: For go_to_min algo
        explorer.update_min_coord()
        x_diff, y_diff = explorer.coord_diff()
        explorer.go_to_min(x_diff, y_diff)

        # Try get feedback from arduino
        feedback = arduino_conn.recv()

        if feedback:
            explorer.obstacle = feedback

        # TODO: For right_wall_hugging algo
        explorer.right_wall_hugging()

        # Send data to arduino everytime there is data in the queue
        if not explorer.dir_queue.empty():
            data = explorer.dir_queue.get()
            arduino_conn.send(data)
            time.sleep(1.5)

        hex_exp_map = explorer.convert_map_to_hex(explorer.explored_map)
        # TODO: Bluetooth & Rasp Pi array here!
        bt_conn.to_send_queue.put([hex_exp_map])
        server_stream.queue.put([recorder.io.read1(1)])

        hex_real_map = explorer.convert_map_to_hex(explorer.real_map)
        server_send.queue.put([hex_real_map])
        explorer.save_map(hex_real_map)


def init(arduino_conn, bt_conn):
    feedback = arduino_conn.recv()
    while not feedback[2]:
        arduino_conn.send('right')
        time.sleep(2)
        feedback = arduino_conn.recv()

    # TODO: Tablet to send array [x, y] of map, i.e. [15, 20] or [20, 15]
    #       [rows, col]
    map_size = bt_conn.have_recv_queue.get()
    return map_size


if __name__ == "__main__":
    import platform
    main(platform.system())

# Import written classes
from RPi.server import Server
from RPi.bluetooth import Bluetooth
from RPi.arduino import Arduino
from RPi.client import Client
from Algo.explore import Explore
from Algo.image_recognition import ImageRecognition
# from Algo.shortest_path import ShortestPath
from config.text_color import TextColor as text_color
from config.state import Direction

# Import libraries
import time
import cv2
import os


def main(sys_type):

    # Initialise required stuff here
    rpi_ip = '192.168.17.17'
    rpi_mac_addr = 'B8:27:EB:52:AC:83'
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
    server_send = Server('server_send', 'send', rpi_ip, 80, text_color)
    server_recv = Server('server_recv', 'recv', rpi_ip, 81, text_color)
    server_stream = Server('server_stream', 'send', rpi_ip, 82, text_color)
    server_send.listen()
    server_recv.listen()
    server_stream.listen()

    # Connect to Tablet
    bt_conn = Bluetooth(rpi_mac_addr, text_color)
    bt_conn.listen()

    while True:
        # Receive data from tablet
        # TODO: Get Arduino, Android and PC to send data in arrays, message to put in index 0
        mode = bt_conn.have_recv_queue.get()[0]

        # 4 modes to accommodate for: Explore, Image Recognition, Shortest Path, Manual and Disconnect
        if mode in ['Explore', 'Image Recognition', 'Shortest Path', 'Manual', 'Disconnect']:

            # Send ack to Android device
            # TODO: Tablet might not be able to send/receive array
            bt_conn.to_send_queue.put(['{} acknowledged'.format(mode)])

            # Display on screen the mode getting executed
            print(log_string + text_color.OKGREEN + '{} Mode Initiated'.format(mode) + text_color.ENDC)

            if mode == 'Explore':
                explore(arduino_conn, bt_conn, server_stream, server_send)

            elif mode == 'Image Recognition':
                print(mode)

            elif mode == 'Shortest Path':
                print(mode)

            elif mode == 'Manual':
                print(mode)

            elif mode == 'Disconnect':
                # Send message to PC and Arduino to tell them to disconnect
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
            print(log_string + text_color.FAIL + 'Invalid message received.' + text_color.ENDC)

            # Add data into queue for sending to tablet
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
    pc_send = Client('pc_send', 'send', rpi_ip, 80, text_color)
    pc_recv = Client('pc_recv', 'recv', rpi_ip, 81, text_color)
    pc_stream = Client('pc_stream', 'recv', rpi_ip, 82, text_color)

    # Connect to Raspberry Pi
    pc_send.connect()
    pc_recv.connect()
    pc_stream.connect()

    while True:

        # Receive data from Raspberry Pi
        data = pc_recv.queue.get()[0]

        # 4 modes to accommodate for: Explore, Image Recognition, Shortest Path, Manual and Disconnect
        if data in ['Explore', 'Image Recognition', 'Shortest Path', 'Manual', 'Disconnect']:

            # Send ack to Raspberry Pi
            pc_send.queue.put(['{} acknowledged'.format(data)])

            # Display on screen the mode getting executed
            print(log_string + text_color.OKGREEN + '{} mode initiated'.format(data) + text_color.ENDC)

            if data == 'Explore':
                while True:

                    # Receive stream from socket
                    # TODO: Do something with explored map (index = 1) and current robot position (index = 2)
                    stream = pc_stream.queue.get()[0]

                    # If end of stream (indicated with return value 0), break
                    if not stream:
                        break

                    # Display stream in a window
                    cv2.imshow('Stream from Pi', stream)

                real_map_hex = pc_recv.queue.get()[0]

                while not real_map_hex:
                    real_map_hex = pc_recv.queue.get()[0]

                exp_map_hex = pc_recv.queue.get()[0]

                while not exp_map_hex:
                    exp_map_hex = pc_recv.queue.get()[0]

                print(log_string + text_color.BOLD +
                      'Real Map Hexadecimal = {}'.format(real_map_hex)
                      + text_color.ENDC)

                print(log_string + text_color.BOLD +
                      'Explored Map Hexadecimal = {}'.format(exp_map_hex)
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
            pc_send.queue.put(['Send valid argument'])


def explore(arduino_conn, bt_conn, server_stream, server_send):

    from RPi.recorder import Recorder

    # Start an instance of Recorder class
    recorder = Recorder()

    # Start recording with the Pi camera
    recorder.start()

    # Start an instance of Explore class
    explorer = Explore()

    # Start an instance of ImageRecognition class
    img_recognisor = ImageRecognition(text_color)

    # Get variables from is_map_complete
    real_map_hex, exp_map_hex = explorer.is_map_complete()

    # While map is not complete, continue streaming data to PC
    while not real_map_hex:

        obstacle = []
        dir_stack = []

        # TODO: For streaming, input from camera (index = 0), explored map (index = 1) and
        #       current position of robot (index = 2) are sent together in an array
        # Try get feedback from arduino
        feedback = arduino_conn.recv()

        # If arduino senses something in front, draw box and try to identify if there is an image
        if feedback:

            # Draw box and capture image
            img = recorder.draw_box()

            # Compare captured image with our own image
            is_img = img_recognisor.compare(img)

            # If captured image is image, send to PC to save
            if is_img:
                server_send.queue.put([img])

            # Remove saved image
            os.remove(img)

            explorer.update_map(explorer.current_pos, obstacle)

        # Update tablet with explored map and current position
        bt_conn.to_send_queue.put([explorer.explored_map, explorer.current_pos])

        # Stream camera input to PC
        server_stream.queue.put([recorder.io.read1(1)])

    # Once map is complete, stop recording
    recorder.stop()

    server_send.queue.put([real_map_hex])
    server_send.queue.put([exp_map_hex])


if __name__ == "__main__":
    import platform
    main(platform.system())

# Import written classes
from RPi.wifi import Wifi
from RPi.bluetooth import Bluetooth
from RPi.arduino import Arduino
from RPi.pc import PC
from RPi.recorder import Recorder
from Algo.explore import Explore
# from Algo.image_recognition import ImageRecognition
# from Algo.shortest_path import ShortestPath
from config.text_color import TextColor as text_color

# Import libraries
import time
import cv2


def main(sys_type):

    # Initialise required stuff here
    rpi_ip = '192.168.17.17'
    port = 80
    rpi_mac_addr = ''
    arduino_name = ''

    log_string = text_color.OKBLUE + "{} | Main: ".format(time.asctime()) + text_color.ENDC

    # If running on Pi, run relevant threads
    if sys_type == 'Linux':
        rpi(rpi_ip, port, rpi_mac_addr, arduino_name, log_string)

    # If running on own PC, run instance of algorithms
    elif sys_type == 'Windows' or sys_type == 'Darwin':
        pc(rpi_ip, port, log_string)

    print(text_color.WARNING + 'End of program reached.' + text_color.ENDC)


def rpi(rpi_ip, port, rpi_mac_addr, arduino_name, log_string):
    """
    Function to start running code on Raspberry Pi
    :param rpi_ip: String
            String containing IP address of Raspberry Pi
    :param port: int
            Int containing port number to be used
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
    wifi_conn = Wifi(rpi_ip, port, text_color)
    wifi_conn.listen()

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
            bt_conn.to_send_queue.put(['{} acknowledged'.format(mode)])

            # Display on screen the mode getting executed
            print(log_string + text_color.OKGREEN + '{} Mode Initiated'.format(mode) + text_color.ENDC)

            # TODO: Add function check_black_box() in Image Recognition to
            #           1. draw box if object in front is >=10% black
            #           2. save image if object in front is >= 25% black
            #       This way Explore can be segregated from ImageRecognition
            if mode == 'Explore':

                # Start an instance of Recorder class
                recorder = Recorder()

                # Start recording with the Pi camera
                recorder.start()

                # Start an instance of Explore class
                explore = Explore()

                real_map_hex, exp_map_hex = explore.is_map_complete()

                # While map is not complete, continue streaming data to PC
                while not real_map_hex:

                    # Put stream into send_queue
                    # TODO: For streaming, input from camera (index = 0), explored map (index = 1) and
                    #       current position of robot (index = 2) are sent together in an array
                    wifi_conn.to_stream_queue.put([recorder.io.read1(1), explore.explored_map, explore.current_pos])

                # Once map is complete, stop recording
                recorder.stop()

                wifi_conn.to_send_queue.put([real_map_hex])
                wifi_conn.to_send_queue.put([exp_map_hex])

            elif mode == 'Image Recognition':
                print(mode)

            elif mode == 'Shortest Path':
                print(mode)

            elif mode == 'Manual':
                print(mode)

            elif mode == 'Disconnect':
                # Send message to PC and Arduino to tell them to disconnect
                wifi_conn.to_send_queue.put(['Disconnect'])
                arduino_conn.to_send_queue.put(['Disconnect'])

                # Wait for 5s to ensure that PC and Arduino receives the message
                time.sleep(5)

                # Disconnect from wifi and bluetooth connection
                wifi_conn.disconnect()
                bt_conn.disconnect()
                return

        else:
            # Display feedback so that user knows this condition is triggered
            print(log_string + text_color.FAIL + 'Invalid message received.' + text_color.ENDC)

            # Add data into queue for sending to tablet
            bt_conn.to_send_queue.put(['Send valid argument'])


def pc(rpi_ip, port, log_string):
    """
    Function to start running code on PC
    :param rpi_ip: String
            String containing IP address of Raspberry Pi
    :param port: int
            Int containing port number to be used
    :param log_string: String
            String containing format of log to be used
    :return:
    """
    # Create an instance of PC
    pc_obj = PC(rpi_ip, port, text_color)

    # Connect to Raspberry Pi
    pc_obj.connect()

    while True:

        # Receive data from Raspberry Pi
        data = pc_obj.have_recv_queue.get()[0]

        # 4 modes to accommodate for: Explore, Image Recognition, Shortest Path, Manual and Disconnect
        if data in ['Explore', 'Image Recognition', 'Shortest Path', 'Manual', 'Disconnect']:

            # Send ack to Raspberry Pi
            pc_obj.to_send_queue.put(['{} acknowledged'.format(data)])

            # Display on screen the mode getting executed
            print(log_string + text_color.OKGREEN + '{} mode initiated'.format(data) + text_color.ENDC)

            if data == 'Explore':
                while True:

                    # Receive stream from socket
                    # TODO: Do something with explored map (index = 1) and current robot position (index = 2)
                    stream = pc_obj.recv_stream_queue.get()[0]

                    # If end of stream (indicated with return value 0), break
                    if not stream:
                        break

                    # Display stream in a window
                    cv2.imshow('Stream from Pi', stream)

                real_map_hex = pc_obj.have_recv_queue.get()[0]

                while not real_map_hex:
                    real_map_hex = pc_obj.have_recv_queue.get()[0]

                exp_map_hex = pc_obj.have_recv_queue.get()[0]

                while not exp_map_hex:
                    exp_map_hex = pc_obj.have_recv_queue.get()[0]

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
                pc_obj.disconnect()
                return

        else:

            # Display feedback so that user knows this condition is triggered
            print(log_string + text_color.FAIL + 'Invalid argument "{}" received.'.format(data) + text_color.ENDC)

            # Add data into queue for sending to Raspberry Pi
            # Failsafe condition
            pc_obj.to_send_queue.put(['Send valid argument'])


if __name__ == "__main__":
    import platform
    main(platform.system())

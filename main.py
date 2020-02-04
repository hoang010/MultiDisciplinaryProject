# Import written classes
from RPi.wifi import Wifi
from RPi.bluetooth import Bluetooth
from RPi.arduino import Arduino
from RPi.pc import PC
# from RPi.Camera import Camera
# from Algo.explore import Explore
# from Algo.image_recognition import ImageRecognition
# from Algo.shortest_path import ShortestPath
from config.text_color import TextColor as text_color

# Import libraries
import time


def main(sys_type):

    # Initialise required stuff here
    rpi_ip = '192.168.17.17'
    port = '80'
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
            bt_conn.to_send_queue.put('{} acknowledged'.format(mode))

            # Display on screen the mode getting executed
            print(log_string + text_color.OKGREEN + '{} Mode Initiated'.format(mode) + text_color.ENDC)

            if mode == 'Explore':
                print(mode)

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
                print(data)

            elif data == 'Image Recognition':
                print(data)

            elif data == 'Shortest Path':
                print(data)

            elif data == 'Manual':
                print(data)

            elif data == 'Disconnect':
                pc_obj.disconnect()
                return

        else:

            # Display feedback so that user knows this condition is triggered
            print(log_string + text_color.FAIL + 'Invalid argument received.' + text_color.ENDC)

            # Add data into queue for sending to Raspberry Pi
            # Failsafe condition
            pc_obj.to_send_queue.put(['Send valid argument'])


if __name__ == "__main__":
    import platform
    main(platform.system())

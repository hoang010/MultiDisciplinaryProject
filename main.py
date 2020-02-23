# Import written classes
from RPi.server import Server
from RPi.bluetooth import Bluetooth
from RPi.arduino import Arduino
from RPi.client import Client
from Algo.explore import Explore
from Algo.image_recognition import ImageRecognition
from Algo.a_star import AStar
# from Algo.shortest_path import ShortestPath
from config.text_color import TextColor as text_color
from config.direction import Direction

# Import libraries
import numpy as np
import time
import cv2
import os


def main(sys_type):
    """
    Main function of MDP Project, execute this file to start
    :param sys_type: String
            String containing System Type (Windows, Linux or Mac)
    :return:
    """

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
    # Initialise variables here
    explorer = None
    
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
    map_size = robo_init(arduino_conn, bt_conn)
    try:
        while True:
            # Receive data from tablet
            mode = bt_conn.have_recv_queue.get()

            mode = mode.decode()

            # 4 modes to accommodate for: Explore, Image Recognition, Shortest Path, Manual and Disconnect
            if mode in ['Explore', 'Image Recognition', 'Shortest Path', 'Manual', 'Disconnect']:

                # Send ack to Android device
                bt_conn.to_send_queue.put(('{} acknowledged'.format(mode)).encode())

                # Display on screen the mode getting executed
                print(log_string + text_color.OKGREEN + '{} Mode Initiated'.format(mode) + text_color.ENDC)

                if mode == 'Explore':
                    explorer = explore(log_string, map_size, arduino_conn, bt_conn, server_stream)

                elif mode == 'Image Recognition':
                    print(mode)

                elif mode == 'Shortest Path':
                    algo = AStar(explorer.real_map, explorer.goal)
                    algo.find_path()
                    path = algo.path
                    for node in path:
                        move_to_point(arduino_conn, explorer, node.ref_pt)

                elif mode == 'Manual':
                    print(mode)

                elif mode == 'Disconnect':
                    # Send message to PC and Arduino to tell them to disconnect
                    server_send.queue.put('Disconnect'.encode())
                    arduino_conn.to_send_queue.put('Disconnect'.encode())

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
                bt_conn.to_send_queue.put('Send valid argument'.encode())

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
    pc_send = Client('pc_send', 'send', rpi_ip, 7777, text_color)
    pc_recv = Client('pc_recv', 'recv', rpi_ip, 8888, text_color)
    pc_stream = Client('pc_stream', 'recv', rpi_ip, 9999, text_color)

    # Connect to Raspberry Pi
    pc_send.connect()
    pc_recv.connect()
    pc_stream.connect()

    try:
        while True:

            # Receive data from Raspberry Pi
            # TODO: Rasp Pi array here!
            data = pc_recv.queue.get()

            data = data.decode()

            # 4 modes to accommodate for: Explore, Image Recognition, Shortest Path, Manual and Disconnect
            if data in ['Explore', 'Image Recognition', 'Shortest Path', 'Manual', 'Info Passing', 'Disconnect']:

                # Send ack to Raspberry Pi
                # TODO: Rasp Pi array here!
                pc_send.queue.put(('{} acknowledged'.format(data)).encode())

                # Display on screen the mode getting executed
                print(log_string + text_color.OKGREEN + '{} mode initiated'.format(data) + text_color.ENDC)

                if data == 'Explore':
                    while True:

                        # Receive stream from socket
                        stream = pc_stream.queue.get()

                        if not stream:
                            break

                        stream = stream.decode()

                        # Display stream in a window
                        cv2.imshow('Stream from Pi', stream)

                    # TODO: Rasp Pi array here!
                    real_map_hex = pc_recv.queue.get()

                    real_map_hex = real_map_hex.decode()

                    print(log_string + text_color.BOLD +
                          'Real Map Hexadecimal = {}'.format(real_map_hex)
                          + text_color.ENDC)

                elif data == 'Image Recognition':
                    pass

                elif data == 'Shortest Path':
                    pass

                elif data == 'Manual':
                    pass

                elif data == 'Disconnect':
                    # Disconnect from Raspberry Pi
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
                pc_send.queue.put('Send valid argument'.encode())

    except KeyboardInterrupt:
        os.system('pkill -9 python')


# This init is done assuming the robot does not start in a "room" in the corner
def robo_init(arduino_conn, bt_conn):
    """
    Function to init robot
    :param arduino_conn: Serial
            Serial class containing connection to Arduino
    :param bt_conn: Socket
            Socket containing connection to tablet0
    :return:
    """
    # Get feedback from Arduino
    feedback = arduino_conn.have_recv_queue.get()

    feedback = feedback.decode()

    front_left_obstacle = int(feedback["TopLeft"]) / 10
    front_mid_obstacle = int(feedback["TopMiddle"]) / 10
    front_right_obstacle = int(feedback["TopRight"]) / 10
    mid_right_obstacle = int(feedback["RightSide"]) / 10

    # While there is no obstacle on the right
    while mid_right_obstacle > 1:

        # If there is no obstacle on the right, tell Arduino to turn right
        arduino_conn.to_send_queue.put('5'.encode())

        # Refresh variables in freedback
        _ = arduino_conn.have_recv_queue.get()

    # If robot is facing corner, turn left
    if (front_left_obstacle <= 1 or front_mid_obstacle <= 1 or front_right_obstacle <= 1) and mid_right_obstacle <= 1:
        arduino_conn.to_send_queue.put('4'.encode())

    # TODO: Tablet to send array [x, y] of map, i.e. [15, 20] or [20, 15]
    #       [rows, col]
    # Get map size from tablet, i.e. (15, 20) or (20, 15)
    map_size = bt_conn.have_recv_queue.get()

    map_size = map_size.decode()

    return map_size


def explore(log_string, map_size, arduino_conn, bt_conn, server_stream):
    """
    Function to run explore algorithm
    :param log_string: String
            Format of log
    :param map_size: Array
            Array containing map size to be used for explore algorithm (15, 20) or (20, 15)
    :param arduino_conn: Serial
            Serial class containing connection to Arduino board
    :param bt_conn: Socket
            Bluetooth Socket containing connection to tablet
    :param server_stream: Socket
            Socket containing connection to PC on port 9999
    :return:
    """

    from RPi.recorder import Recorder

    # Start an instance of Recorder class
    recorder = Recorder()

    # Start recording with the Pi camera
    recorder.start()

    # Start an instance of Explore class
    explorer = Explore(map_size, Direction)

    # Start an instance of ImageRecognition class
    img_recognisor = ImageRecognition(text_color)

    print(log_string + text_color.OKGREEN + 'Explore started' + text_color.ENDC)

    # While map is not complete
    while not explorer.is_map_complete():

        # While round is not complete
        while explorer.check_round_complete():

            print(log_string + text_color.WARNING + 'Round not completed' + text_color.ENDC)

            print(log_string + text_color.BOLD + 'Getting sensor data' + text_color.ENDC)

            # Get sensor data
            send_param = '2'.encode()
            arduino_conn.to_send_queue.put(send_param)
            sensor_data = arduino_conn.have_recv_queue.get()

            print(log_string + text_color.OKGREEN + 'Sensor data received' + text_color.ENDC)

            # Start hugging right wall to explore
            explorer.right_wall_hugging(sensor_data)

            # Get next movement
            movement = explorer.move_queue.get()

            # Display message
            if movement == '5':
                log_movement = 'right'
            elif movement == '4':
                log_movement = 'left'
            else:
                log_movement = 'forward'
            print(log_string + text_color.BOLD + 'Moving {}'.format(log_movement) + text_color.ENDC)

            # Encode before sending to arduino
            movement = movement.encode()
            arduino_conn.to_send_queue.put(movement)

            # Get feedback from Arduino
            _ = arduino_conn.have_recv_queue.get()
            print(log_string + text_color.OKGREEN + 'Arduino ack received' + text_color.ENDC)

            # Convert explored map into hex
            hex_exp_map = explorer.convert_map_to_hex(explorer.explored_map)
            print(log_string + text_color.BOLD + 'Explore hex map: {}'.format(hex_exp_map) + text_color.ENDC)

            # Send hex explored map to tablet
            hex_exp_map = hex_exp_map.encode()
            bt_conn.to_send_queue.put(hex_exp_map)
            print(log_string + text_color.OKGREEN + 'Hex map sent to tablet' + text_color.ENDC)

            # Get camera input and encode it into hex
            stream = recorder.io.read1(1)
            stream_byte = stream.encode()

            # Send stream to PC
            server_stream.queue.put(stream_byte)
            print(log_string + text_color.OKBLUE + 'Stream data sent to PC' + text_color.ENDC)

        # If round is complete, shift starting position
        explorer.update_start(3, 3)
        print(log_string + text_color.OKGREEN + 'Round completed' + text_color.ENDC)
        print(log_string + text_color.BOLD + 'Updated start by 3' + text_color.ENDC)

        # Actually move to new start position
        move_to_point(log_string, arduino_conn, explorer, explorer.start)

        # If start has obstacle, shift again
        while not check_start(explorer, explorer.start):
            print(log_string + text_color.WARNING + 'Obstacle encountered' + text_color.ENDC)
            explorer.update_start(1, 0)
            print(log_string + text_color.BOLD + 'Updated start by 1 in x direction' + text_color.ENDC)

        # Move to new start
        move_to_point(log_string, arduino_conn, explorer, explorer.start)

    # Send empty packet to tell PC that stream has stopped
    server_stream.queue.put('')

    # Convert real map to hex
    hex_real_map = explorer.convert_map_to_hex(explorer.real_map)

    # Move to initial start
    move_to_point(log_string, arduino_conn, explorer, explorer.true_start)

    # Save real map once done exploring
    explorer.save_map(hex_real_map)

    return explorer


def move_to_point(log_string, arduino_conn, explorer, start):
    """
    Function to move robot to the specified point
    :param log_string: String
            String containing format for log
    :param arduino_conn: Serial
            Connection to Arduino via USB
    :param explorer: Explorer class
            Data in the explorer instance is required
    :param start: Array
            Start point, can be all 9 points of position or just 1 reference start point
    :return:
    """

    # Get difference between x and y coordinates of current position
    # and start position
    if len(start) > 1:
        start_ref = start[4]
    else:
        start_ref = start

    print(log_string + text_color.WARNING + 'Move to point {}'.format(start_ref) + text_color.ENDC)

    # Execute loop while difference is not zero
    while not check_start(explorer, start):

        print(log_string + text_color.BOLD + 'Get sensor data' + text_color.ENDC)

        # Get info about surrounding
        send_param = '2'.encode()
        arduino_conn.to_send_queue.put(send_param)
        sensor_data = arduino_conn.have_recv_queue.get()

        print(log_string + text_color.OKGREEN + 'Sensor data received' + text_color.ENDC)

        # Get the data
        front_left_obstacle = int(sensor_data["TopLeft"]) / 10
        front_mid_obstacle = int(sensor_data["TopMiddle"]) / 10
        front_right_obstacle = int(sensor_data["TopRight"]) / 10
        mid_left_obstacle = int(sensor_data["LeftSide"]) / 10
        mid_right_obstacle = int(sensor_data["RightSide"]) / 10

        # Check if start has obstacle
        front_coord = explorer.get_coord('front')
        start_has_obstacle = ((front_coord[0][0] + front_left_obstacle) in start or
                              (front_coord[1][0] + front_mid_obstacle) in start or
                              (front_coord[2][0] + front_right_obstacle) in start)

        # If there is, update start by 1 in x direction and skip the loop
        if start_has_obstacle:
            print(log_string + text_color.WARNING + 'Obstacle encountered' + text_color.ENDC)
            explorer.update_start(1, 0)
            print(log_string + text_color.BOLD + 'Updated start by 1 in x direction' + text_color.ENDC)
            continue

        # Check if front has obstacle
        front_obstacle = (front_left_obstacle < 1 or front_mid_obstacle < 1 or front_right_obstacle < 1)

        # If there is an obstacle in front
        if front_obstacle:

            # If there is no obstacle on the left
            if not mid_left_obstacle:

                print(log_string + text_color.BOLD + 'Turning left' + text_color.ENDC)

                # Tell Arduino to turn left
                movement = '4'.encode()

                # Update direction
                explorer.update_dir(True)

            # If there is obstacle on both left and right
            elif mid_right_obstacle:

                # This shouldn't happen, but raise error if it does
                raise Exception('GG: Dead End!')

            # If there is obstacle in front and no obstacle on right
            else:

                print(log_string + text_color.BOLD + 'Turning right' + text_color.ENDC)
                # Turn right
                movement = '5'.encode()

                # Update direction
                explorer.update_dir(False)

        # If no obstacle in front
        else:

            # Advance
            print(log_string + text_color.BOLD + 'Moving forward' + text_color.ENDC)
            movement = '3'.encode()

            explorer.update_pos()

        # Tell arduino desired movement
        arduino_conn.to_send_queue.put(movement)

        # Get feedback
        _ = arduino_conn.have_recv_queue.get()


def check_start(explorer, start):
    """
    Function to check if robot is at shifted start
    :param explorer: Explorer class
            Explorer instance as data from it is needed
    :param start: Array
            Coordinates of start position
    :return:
    """
    if len(start) > 2:
        if explorer.current_pos[4] == start[4]:
            return True
    else:
        if explorer.current_pos[4] == start:
            return True
    return False


if __name__ == "__main__":
    import platform
    try:
        main(platform.system())
        # main('Windows')
    except KeyboardInterrupt:
        os.system('pkill -9 python')

# Import written classes
from RPi.server import Server
from RPi.bluetooth import Bluetooth
from RPi.arduino import Arduino
from RPi.client import Client
from Algo.explore import Explore
from Algo.image_recognition import ImageRecognition
# from Algo.a_star import AStar
# from Algo.shortest_path import ShortestPath
from Algo.fastest_path import *
from config.text_color import TextColor as text_color
from config.direction import Direction

# Import libraries
from ast import literal_eval
import json
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
    try:
        while True:
            # Receive data from tablet
            mode = bt_conn.have_recv_queue.get()

            mode = mode.decode()

            # 4 modes to accommodate for: Explore, Image Recognition, Shortest Path, Manual and Disconnect
            if mode in ['beginExplore', 'Image Recognition', 'beginFastest', 'Manual', 'Disconnect']:

                # Send ack to Android device
                bt_conn.to_send_queue.put(('{} acknowledged'.format(mode)).encode())

                # Display on screen the mode getting executed
                print(log_string + text_color.OKGREEN + '{} Mode Initiated'.format(mode) + text_color.ENDC)

                if mode == 'beginExplore':
                    explorer = explore(log_string, arduino_conn, bt_conn, server_stream)

                elif mode == 'Image Recognition':
                    print(mode)

                elif mode == 'beginFastest':
                    waypt = bt_conn.have_recv_queue.get()
                    waypt = waypt.decode()

                    flag = 0

                    for i in range(2):
                        a_star = AStar(explorer.start, waypt, explorer.real_map)
                        start_pt = AStar.Node(explorer.start, waypt, 0)
                        a_star.open_list.append(start_pt)

                        while not flag:
                            a_star_current = a_star.select_current()
                            flag = a_star.near_explore(a_star_current)

                        for node_path in a_star.path:
                            explorer.move_to_point(log_string, text_color, arduino_conn, node_path.point)

                        explorer.start = explorer.current_pos
                        waypt = explorer.goal

                    # algo = AStar(explorer.real_map, explorer.goal)
                    # algo.find_path()
                    # path = algo.path
                    # for node in path:
                    #     explorer.move_to_point(log_string, arduino_conn, explorer, node.ref_pt)

                elif mode == 'Manual':
                    while True:
                        manual_explorer = Explore(Direction)
                        movement = bt_conn.have_recv_queue.get()

                        movement = movement.decode()

                        if movement == 'sl':
                            print(log_string + text_color.BOLD + 'Turn left' + text_color.ENDC)
                            arduino_conn.to_send_queue.put(b'4')
                            arduino_conn.have_recv_queue.get()
                            manual_explorer.update_dir(True)

                        elif movement == 'f':
                            print(log_string + text_color.BOLD + 'Move forward' + text_color.ENDC)
                            arduino_conn.to_send_queue.put(b'3')
                            arduino_conn.have_recv_queue.get()
                            manual_explorer.update_pos(True)

                        elif movement == 'sr':
                            print(log_string + text_color.BOLD + 'Turn right' + text_color.ENDC)
                            arduino_conn.to_send_queue.put(b'5')
                            arduino_conn.have_recv_queue.get()
                            manual_explorer.update_dir(False)

                        elif movement == 'tl':
                            print(log_string + text_color.BOLD + 'Rotate left' + text_color.ENDC)
                            arduino_conn.to_send_queue.put(b'7')
                            arduino_conn.have_recv_queue.get()
                            manual_explorer.update_dir(True)
                            manual_explorer.update_dir(True)

                        elif movement == 'r':
                            print(log_string + text_color.BOLD + 'Move backwards' + text_color.ENDC)
                            arduino_conn.to_send_queue.put(b'6')
                            arduino_conn.have_recv_queue.get()
                            manual_explorer.update_pos(False)

                        elif movement == 'tr':
                            print(log_string + text_color.BOLD + 'Rotate right' + text_color.ENDC)
                            arduino_conn.to_send_queue.put(b'8')
                            arduino_conn.have_recv_queue.get()
                            manual_explorer.update_dir(False)
                            manual_explorer.update_dir(False)

                        elif movement == 'end':
                            break

                        else:
                            print(log_string + text_color.FAIL + 'Command unrecognised' + text_color.ENDC)

                        bt_conn.to_send_queue.put(manual_explorer.direction.encode())
                        bt_conn.to_send_queue.put(manual_explorer.current_pos.encode())

                    print(log_string + text_color.WARNING + 'Manual mode terminated' + text_color.ENDC)

                elif mode == 'Disconnect':
                    # Send message to PC and Arduino to tell them to disconnect
                    server_send.queue.put('Disconnect'.encode())
                    arduino_conn.to_send_queue.put('Disconnect'.encode())

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
    pc_recv = Client('pc_recv', 'recv', rpi_ip, 7777, text_color)
    pc_send = Client('pc_send', 'send', rpi_ip, 8888, text_color)
    pc_stream = Client('pc_stream', 'recv', rpi_ip, 9999, text_color)

    # Connect to Raspberry Pi
    pc_recv.connect()
    pc_send.connect()
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
def robo_init(arduino_conn):
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

    feedback = literal_eval(feedback.decode())
    feedback = json.dumps(feedback, indent=4, sort_keys=True)

    front_left_obstacle = int(feedback["TopLeft"]) / 10
    front_mid_obstacle = int(feedback["TopMiddle"]) / 10
    front_right_obstacle = int(feedback["TopRight"]) / 10
    mid_right_obstacle = int(feedback["RightSide"]) / 10

    # While there is no obstacle on the right
    while mid_right_obstacle > 1:

        # If there is no obstacle on the right, tell Arduino to turn right
        arduino_conn.to_send_queue.put(b'5')

        # Refresh variables in freedback
        _ = arduino_conn.have_recv_queue.get()

    # If robot is facing corner, turn left
    if (front_left_obstacle <= 1 or front_mid_obstacle <= 1 or front_right_obstacle <= 1) and mid_right_obstacle <= 1:
        arduino_conn.to_send_queue.put(b'4')


def explore(log_string, arduino_conn, bt_conn, server_stream):
    """
    Function to run explore algorithm
    :param log_string: String
            Format of log
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
    explorer = Explore(Direction)

    # Start an instance of ImageRecognition class
    img_recognisor = ImageRecognition(text_color)

    print(log_string + text_color.OKGREEN + 'Explore started' + text_color.ENDC)

    # While map is not complete
    while not explorer.is_map_complete():

        # While round is not complete
        while not explorer.check_round_complete():

            print(log_string + text_color.WARNING + 'Round not completed' + text_color.ENDC)

            print(log_string + text_color.BOLD + 'Getting sensor data' + text_color.ENDC)

            # Get sensor data
            send_param = b'2'
            arduino_conn.to_send_queue.put(send_param)
            sensor_data = arduino_conn.have_recv_queue.get()

            sensor_data = literal_eval(sensor_data)
            sensor_data = json.dumps(sensor_data, indent=4, sort_keys=True)

            print(log_string + text_color.OKGREEN + 'Sensor data received' + text_color.ENDC)

            # Start hugging right wall to explore
            explorer.right_wall_hugging(sensor_data)

            # Get next movement
            movement = explorer.move_queue.get()

            # Display message
            if movement == b'5':
                log_movement = 'right'
            elif movement == b'4':
                log_movement = b'left'
            else:
                log_movement = 'forward'
            print(log_string + text_color.BOLD + 'Moving {}'.format(log_movement) + text_color.ENDC)

            # Send to arduino
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
            bt_conn.to_send_queue.put(explorer.direction)
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
        explorer.move_to_point(log_string, text_color, arduino_conn, explorer.start)

    # Send empty packet to tell PC that stream has stopped
    server_stream.queue.put('')

    # Convert real map to hex
    hex_real_map = explorer.convert_map_to_hex(explorer.real_map)

    # Move to initial start
    explorer.move_to_point(log_string, text_color, arduino_conn, explorer.true_start)

    # Save real map once done exploring
    explorer.save_map(hex_real_map)

    return explorer


if __name__ == "__main__":
    import platform
    try:
        main(platform.system())
        # main('Windows')
    except KeyboardInterrupt:
        os.system('pkill -9 python')

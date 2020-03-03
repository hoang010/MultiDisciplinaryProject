# Import written classes
from RPi.server import Server
from RPi.bluetooth import Bluetooth
from RPi.arduino import Arduino
from RPi.client import Client
from Algo.explore import Explore
# from Algo.image_recognition import ImageRecognition
# from Algo.a_star import AStar
# from Algo.shortest_path import ShortestPath
from Algo.fastest_path import *
from config.text_color import TextColor as text_color
from config.direction import Direction

# Import libraries
import json
import time
import cv2
import os
import math


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
    arduino_name = '/dev/ttyACM0'

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
            if mode in ['beginExplore', 'imageRecognition', 'beginFastest', 'manual', 'disconnect']:

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

                    waypt = json.loads(waypt)

                    waypt_coord = (waypt['x'], waypt['y'])

                    flag = 0

                    for _ in range(2):
                        a_star = AStar(explorer.start[4], waypt_coord, explorer.real_map)
                        start_pt = AStar.Node(explorer.start[4], waypt_coord, 0)
                        a_star.open_list.append(start_pt)

                        while not flag:
                            a_star_current = a_star.select_current()
                            flag = a_star.near_explore(a_star_current)

                        for node_path in a_star.path:
                            move_to_point(log_string, text_color, explorer, arduino_conn, node_path.point)

                        explorer.start = explorer.current_pos
                        waypt_coord = explorer.goal[4]

                elif mode == 'manual':
                    while True:
                        movement = bt_conn.have_recv_queue.get()

                        movement = movement.decode()

                        if movement == 'tl':
                            print(log_string + text_color.BOLD + 'Turn left' + text_color.ENDC)
                            arduino_conn.to_send_queue.put(b'4')
                            arduino_conn.have_recv_queue.get()

                        elif movement == 'f':
                            print(log_string + text_color.BOLD + 'Move forward' + text_color.ENDC)
                            arduino_conn.to_send_queue.put(b'3')
                            arduino_conn.have_recv_queue.get()

                        elif movement == 'tr':
                            print(log_string + text_color.BOLD + 'Turn right' + text_color.ENDC)
                            arduino_conn.to_send_queue.put(b'5')
                            arduino_conn.have_recv_queue.get()

                        elif movement == 'r':
                            print(log_string + text_color.BOLD + 'Move backwards' + text_color.ENDC)
                            arduino_conn.to_send_queue.put(b'6')
                            arduino_conn.have_recv_queue.get()

                        elif movement == 'end':
                            break

                        else:
                            print(log_string + text_color.FAIL + 'Command unrecognised' + text_color.ENDC)

                    print(log_string + text_color.WARNING + 'Manual mode terminated' + text_color.ENDC)

                elif mode == 'disconnect':
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
        arduino_conn.disconnect()
        server_stream.disconnect()
        server_send.disconnect()
        server_recv.disconnect()
        bt_conn.disconnect()
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
            if data in ['beginExplore', 'imageRecognition', 'beginFastest', 'manual', 'disconnect']:

                # Send ack to Raspberry Pi
                # TODO: Rasp Pi array here!
                pc_send.queue.put(('{} acknowledged'.format(data)).encode())

                # Display on screen the mode getting executed
                print(log_string + text_color.OKGREEN + '{} mode initiated'.format(data) + text_color.ENDC)

                if data == 'Explore':
                    pass

                    # # TODO: Rasp Pi array here!
                    # real_map_hex = pc_recv.queue.get()
                    #
                    # real_map_hex = real_map_hex.decode()
                    #
                    # print(log_string + text_color.BOLD +
                    #       'Real Map Hexadecimal = {}'.format(real_map_hex)
                    #       + text_color.ENDC)

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

    sensor_data = json.loads(feedback.decode().strip())

    # Get the data
    front_left_obstacle = math.floor(sensor_data["FrontLeft"]) / 10
    front_mid_obstacle = math.floor(sensor_data["FrontCenter"]) / 10
    front_right_obstacle = math.floor(sensor_data["FrontRight"]) / 10
    right_front_obstacle = math.floor(sensor_data["RightFront"]) / 10
    right_back_obstacle = math.floor(sensor_data["RightBack"]) / 10

    # While there is no obstacle on the right
    while right_front_obstacle > 1 and right_back_obstacle > 1:

        # If there is no obstacle on the right, tell Arduino to turn right
        arduino_conn.to_send_queue.put(b'5')

        # Refresh variables in freedback
        _ = arduino_conn.have_recv_queue.get()

    # If robot is facing corner, turn left
    if (front_left_obstacle <= 1 or front_mid_obstacle <= 1 or front_right_obstacle <= 1) and \
            right_front_obstacle <= 1 and right_back_obstacle <= 1:
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
    # recorder = Recorder()

    # Start recording with the Pi camera
    # recorder.start()

    # Start an instance of Explore class
    explorer = Explore(Direction)

    print(log_string + text_color.OKGREEN + 'Explore started' + text_color.ENDC)

    # While map is not complete
    while not explorer.is_map_complete():

        right_counter = 0

        # While round is not complete
        while not explorer.check_round_complete():

            print(log_string + text_color.WARNING + 'Round not completed' + text_color.ENDC)

            print(log_string + text_color.BOLD + 'Getting sensor data' + text_color.ENDC)

            # Get sensor data
            send_param = b'2'
            arduino_conn.to_send_queue.put(send_param)
            sensor_data = arduino_conn.have_recv_queue.get()

            sensor_data = sensor_data.decode().strip()

            sensor_data = json.loads(sensor_data)

            print(log_string + text_color.OKGREEN + 'Sensor data received' + text_color.ENDC)

            # Start hugging right wall to explore
            explorer.right_wall_hugging(sensor_data)

            # Get next movement
            movement = explorer.move_queue.get()

            # Display message
            if movement == b'5':
                log_movement = 'right'
                right_counter += 1

            elif movement == b'4':
                # get_image(log_string, explorer, arduino_conn)
                log_movement = b'left'
                front_left_obstacle = math.floor(sensor_data["TopLeft"]) / 10
                front_mid_obstacle = math.floor(sensor_data["TopMiddle"]) / 10
                front_right_obstacle = math.floor(sensor_data["TopRight"]) / 10

                if front_left_obstacle < 1 and front_right_obstacle < 1 and front_mid_obstacle < 1:
                    print(log_string + text_color.WARNING + 'Recalibrating corner' + text_color.ENDC)
                    arduino_conn.to_send_queue.put(b'10')
                    arduino_conn.have_recv_queue.get()
                    print(log_string + text_color.OKGREEN + 'Recalibrate corner done' + text_color.ENDC)
            else:
                log_movement = 'forward'

            print(log_string + text_color.BOLD + 'Moving {}'.format(log_movement) + text_color.ENDC)

            # Send to arduino
            arduino_conn.to_send_queue.put(movement)

            # Get feedback from Arduino
            _ = arduino_conn.have_recv_queue.get()

            # Convert explored map into hex
            hex_exp_map = explorer.convert_map_to_hex(explorer.explored_map)
            hex_real_map = explorer.convert_map_to_hex(explorer.real_map)

            packet = str({
                "explored": hex_exp_map,
                "obstacle": hex_real_map,
                "direction": explorer.direction,
                "movement": log_movement[0]
            })

            bt_conn.to_send_queue.put(packet.encode())
            print(log_string + text_color.OKGREEN + 'Packet sent to tablet' + text_color.ENDC)

            # TODO: Send image to PC
            # server_stream.queue.put(stream_byte)
            # print(log_string + text_color.OKBLUE + 'Stream data sent to PC' + text_color.ENDC)

            if right_counter == 5:
                print(log_string + text_color.WARNING + 'Recalibrating right wall' + text_color.ENDC)
                arduino_conn.to_send_queue.put(b'11')
                arduino_conn.have_recv_queue.get()
                right_counter = 0
                print(log_string + text_color.OKGREEN + 'Recalibrate right wall done' + text_color.ENDC)

        # If round is complete, shift starting position
        explorer.update_start(3, 3)
        print(log_string + text_color.OKGREEN + 'Round completed' + text_color.ENDC)
        print(log_string + text_color.BOLD + 'Updated start by 3' + text_color.ENDC)

        # Actually move to new start position
        explorer.navigate_to_point(log_string, text_color, arduino_conn, explorer.start)

    print(log_string + text_color.OKGREEN + 'Explore completed' + text_color.ENDC)

    # Send empty packet to tell PC that stream has stopped
    # server_stream.queue.put('')

    # Convert real map to hex
    hex_real_map = explorer.convert_map_to_hex(explorer.real_map)

    packet = str({
        "obstacle": hex_real_map
    })

    bt_conn.to_send_queue.put(packet.encode())

    # Move to initial start
    explorer.navigate_to_point(log_string, text_color, arduino_conn, explorer.true_start)

    # Save real map once done exploring
    explorer.save_map(hex_real_map)

    return explorer


def get_image(log_string, explorer, arduino_conn):
    start_pos = explorer.current_pos
    start_dir = explorer.direction

    while True:
        send_param = b'2'
        arduino_conn.to_send_queue.put(send_param)
        sensor_data = arduino_conn.have_recv_queue.get()

        sensor_data = json.loads(sensor_data.decode().strip())

        # Get the data
        front_left_obstacle = math.floor(sensor_data["FrontLeft"]) / 10
        front_mid_obstacle = math.floor(sensor_data["FrontCenter"]) / 10
        front_right_obstacle = math.floor(sensor_data["FrontRight"]) / 10
        mid_left_obstacle = math.floor(sensor_data["LeftSide"]) / 10
        right_front_obstacle = math.floor(sensor_data["RightFront"]) / 10
        right_back_obstacle = math.floor(sensor_data["RightBack"]) / 10

        # Camera facing right
        # Turn left
        arduino_conn.to_send_queue.put(b'4')
        arduino_conn.have_recv_queue.get()

        # Insert image recog code here
        # TODO: This is a placeholder!
        captured = ImageRecognition(text_color)

        if captured:
            explorer.navigate_to_point(log_string, text_color, arduino_conn, start_pos)
            break

        else:
            # If no obstacle on right
            if right_front_obstacle > 2 or right_back_obstacle > 2:
                arduino_conn.to_send_queue.put(b'5')
                arduino_conn.have_recv_queue.get()

            # If front has obstacle
            elif front_left_obstacle < 2 or front_mid_obstacle < 2 or front_right_obstacle < 2:
                # Turn left
                arduino_conn.to_send_queue.put(b'4')
                arduino_conn.have_recv_queue.get()

            else:
                # Advance
                arduino_conn.to_send_queue.put(b'3')
                arduino_conn.have_recv_queue.get()

    while not explorer.set_direction(start_dir):
        continue


def move_to_point(log_string, text_color, explorer, arduino_conn, point):

    # Comparing x axis
    if explorer.current_pos[4][0] != point[0]:
        more = explorer.current_pos[4][0] - point[0]

        # Turn left if more
        if more > 0:
            print(log_string + text_color.OKBLUE + 'Turning left' + text_color.ENDC)
            arduino_conn.to_send_queue.put(b'4')
            arduino_conn.have_recv_queue.get()

            print(log_string + text_color.OKBLUE + 'Moving forward' + text_color.ENDC)
            arduino_conn.to_send_queue.put(b'3')
            arduino_conn.have_recv_queue.get()

        # Turn right if less
        else:
            print(log_string + text_color.OKBLUE + 'Turning right' + text_color.ENDC)
            arduino_conn.to_send_queue.put(b'5')
            arduino_conn.have_recv_queue.get()

            print(log_string + text_color.OKBLUE + 'Moving forward' + text_color.ENDC)
            arduino_conn.to_send_queue.put(b'3')
            arduino_conn.have_recv_queue.get()

    # Comparing y axis
    elif explorer.current_pos[4][1] != point[1]:
        more = explorer.current_pos[4][1] - point[1]

        # Move forward if more
        if more > 0:
            print(log_string + text_color.OKBLUE + 'Moving forward' + text_color.ENDC)
            arduino_conn.to_send_queue.put(b'3')
            arduino_conn.have_recv_queue.get()

        # Move backward if less
        else:
            print(log_string + text_color.OKBLUE + 'Moving backward' + text_color.ENDC)
            arduino_conn.to_send_queue.put(b'6')
            arduino_conn.have_recv_queue.get()


if __name__ == "__main__":
    import platform
    try:
        main(platform.system())
        # main('Windows')
    except KeyboardInterrupt:
        os.system('pkill -9 python')

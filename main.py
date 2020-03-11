# Import written classes
from RPi.server import Server
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
    from RPi.bluetooth import Bluetooth
    
    # Connect to Arduino
    arduino_conn = Arduino(arduino_name, text_color)

    # Connect to PC
    server_conn = Server(rpi_ip, 7777, text_color)
    server_conn.listen()

    # Connect to Tablet
    bt_conn = Bluetooth(rpi_mac_addr, text_color)
    bt_conn.listen()
    try:
        while True:
            # Receive data from tablet
            mode = bt_conn.recv_channel()

            mode = mode.decode()

            # 4 modes to accommodate for: Explore, Image Recognition, Shortest Path, Manual and Disconnect
            if mode in ['beginExplore', 'imageRecognition', 'beginFastest', 'manual', 'disconnect']:

                # Display on screen the mode getting executed
                print(log_string + text_color.OKGREEN + '{} Mode Initiated'.format(mode) + text_color.ENDC)

                if mode == 'beginExplore':
                    robo_init(log_string, arduino_conn, bt_conn)
                    server_conn.send_channel(mode.encode())
                    server_conn.recv_channel()

                    while True:
                        feedback = server_conn.recv_channel()
                        server_conn.send_channel('ack'.encode())
                        feedback = feedback.decode()
                        if feedback == 'end':
                            break
                        feedback = json.loads(feedback)

                        if feedback["dest"] == "arduino":
                            param = feedback["param"]
                            arduino_conn.send_channel(param.encode())
                            if param != "11" or param != "12":
                                msg = arduino_conn.recv_channel()
                                server_conn.send_channel(msg)

                        elif feedback["dest"] == "bt":
                            del feedback["dest"]
                            feedback = str(feedback)
                            bt_conn.send_channel(feedback.encode())

                elif mode == 'Image Recognition':
                    print(mode)

                elif mode == 'beginFastest':
                    waypt = bt_conn.recv_channel()
                    server_conn.send_channel(waypt)
                    path = server_conn.recv_channel()
                    path = json.loads(path.decode())
                    for ele in path:
                        arduino_conn.send_channel(ele)

                elif mode == 'manual':
                    server_conn.to_send_queue.put('manual'.encode())
                    while True:
                        msg = bt_conn.recv_channel()
                        server_conn.send_channel(msg)
                        msg = msg.decode()
                        if msg == 'end':
                            print(log_string + text_color.OKGREEN + 'Explore ended' + text_color.ENDC)
                            break
                        movement = server_conn.recv_channel()
                        arduino_conn.send_channel(movement)
                        arduino_conn.recv_channel()

                elif mode == 'disconnect':
                    # Send message to PC and Arduino to tell them to disconnect
                    server_conn.send_channel('Disconnect'.encode())
                    arduino_conn.send_channel('Disconnect'.encode())

                    # Disconnect from wifi and bluetooth connection
                    server_conn.disconnect()
                    arduino_conn.disconnect()
                    bt_conn.disconnect()
                    return

            else:
                # Display feedback so that user knows this condition is triggered
                print(log_string + text_color.FAIL +
                      'Invalid message {} received.'.format(mode)
                      + text_color.ENDC)

                # Add data into queue for sending to tablet
                bt_conn.send_channel('Send valid argument'.encode())

    except KeyboardInterrupt:
        arduino_conn.disconnect()
        server_conn.disconnect()
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
    pc_conn = Client(rpi_ip, 7777, text_color)

    # Connect to Raspberry Pi
    pc_conn.connect()

    explorer = None

    try:
        while True:

            # Receive data from Raspberry Pi
            # TODO: Rasp Pi array here!
            data = pc_conn.recv_channel()

            data = data.decode()

            # 4 modes to accommodate for: Explore, Image Recognition, Shortest Path, Manual and Disconnect
            if data in ['beginExplore', 'imageRecognition', 'beginFastest', 'manual', 'disconnect']:

                # Send ack to Raspberry Pi
                # TODO: Rasp Pi array here!
                pc_conn.send_channel(('{} acknowledged'.format(data)).encode())

                # Display on screen the mode getting executed
                print(log_string + text_color.OKGREEN + '{} mode initiated'.format(data) + text_color.ENDC)

                if data == 'beginExplore':
                    explorer = explore(log_string, pc_conn)

                elif data == 'imageRecognition':
                    pass

                elif data == 'beginFastest':
                    waypt = pc_conn.recv_channel()
                    waypt = waypt.decode()

                    waypt = json.loads(waypt)
                    waypt_coord = [waypt['x'], waypt['y']]

                    flag = 0

                    path = []

                    for _ in range(2):
                        a_star = AStar(explorer.start[4], waypt_coord, explorer.real_map)
                        start_pt = AStar.Node(explorer.start[4], waypt_coord, 0)
                        a_star.open_list.append(start_pt)

                        while not flag:
                            a_star_current = a_star.select_current()
                            flag = a_star.near_explore(a_star_current)

                        for node_path in a_star.path:
                            movements = move_to_point(explorer, node_path.point)
                            for ele in movements:
                                path.append(ele)

                        explorer.start = explorer.current_pos
                        waypt_coord = explorer.goal[4]

                    path_string = '{'
                    for i in range(len(path)):
                        if path[i] == 3:
                            count = 1
                            while path[i] == 3:
                                count += 1
                                i += 1
                            path_string += '{}: {}'.format('3', str(count*10))
                            i -= 1
                        else:
                            path_string += '{}: {}'.format(path[i], '90')
                    path_string = path_string[:-1]
                    path_string += '}'

                    send_param = "{\"dest\": \"arduino\",\"param\": \"" + path_string + "\" }"
                    pc_conn.send_channel(send_param.encode())

                elif data == 'manual':
                    while True:
                        movement = pc_conn.recv_channel()

                        movement = movement.decode()

                        if movement == 'tl':
                            print(log_string + text_color.BOLD + 'Turn left' + text_color.ENDC)
                            pc_conn.send_channel("4")

                        elif movement == 'f':
                            print(log_string + text_color.BOLD + 'Move forward' + text_color.ENDC)
                            pc_conn.send_channel("3")

                        elif movement == 'tr':
                            print(log_string + text_color.BOLD + 'Turn right' + text_color.ENDC)
                            pc_conn.send_channel("5")

                        elif movement == 'r':
                            print(log_string + text_color.BOLD + 'Move backwards' + text_color.ENDC)
                            pc_conn.send_channel("6")

                        elif movement == 'end':
                            break

                        else:
                            print(log_string + text_color.FAIL + 'Command unrecognised' + text_color.ENDC)

                    print(log_string + text_color.WARNING + 'Manual mode terminated' + text_color.ENDC)

                elif data == 'disconnect':
                    # Disconnect from Raspberry Pi
                    pc_conn.disconnect()
                    return

            else:

                # Display feedback so that user knows this condition is triggered
                print(log_string + text_color.FAIL + 'Invalid argument "{}" received.'.format(data) + text_color.ENDC)

                # Add data into queue for sending to Raspberry Pi
                # Failsafe condition
                pc_conn.send_channel('Send valid argument'.encode())

    except KeyboardInterrupt:
        pc_conn.disconnect()
        os.system('pkill -9 python')


def robo_init(log_string, arduino_conn, bt_conn):
    """
    Function to init robot, to be called by Raspberry Pi

    :param log_string: String
            String containing logs
    :param arduino_conn: Serial
            Serial class containing connection to Arduino
    :param bt_conn: Socket
            Socket containing connection to tablet0
    :return:
    """

    print(log_string + text_color.WARNING + 'Initialising' + text_color.ENDC)

    packet = "{\"dest\": \"bt\",\"movement\": \"l\",\"direction\": \"" + Direction.N + "\" }"
    bt_conn.to_send_queue.put(packet.encode())

    arduino_conn.send_channel(b'13')
    arduino_conn.recv_channel()
    print(log_string + text_color.OKGREEN + 'Initialising done' + text_color.ENDC)


def explore(log_string, pc_conn):
    """
    Function to run explore algorithm
    :param log_string: String
            Format of log
    :param pc_conn: Socket
            Socket containing connection between PC and RPi
    :return:
    """

    # Start an instance of Explore class
    explorer = Explore(Direction)

    print(log_string + text_color.OKGREEN + 'Explore started' + text_color.ENDC)
    
    right_wall_counter = 0

    print(log_string + text_color.BOLD + 'Getting sensor data' + text_color.ENDC)

    # Get sensor data
    send_param = "{\"dest\":\"arduino\",\"param\":\"2\"}"
    pc_conn.send_channel(send_param.encode())
    pc_conn.recv_channel()

    # While map is not complete
    while not explorer.is_map_complete():

        print(log_string + text_color.WARNING + 'Round not completed' + text_color.ENDC)

        sensor_data = pc_conn.recv_channel()
        sensor_data = sensor_data.decode().strip()
        sensor_data = json.loads(sensor_data)

        explorer.sensor_data_queue.put(sensor_data)
        print(log_string + text_color.OKGREEN + 'Sensor data received' + text_color.ENDC)

        # Get next movement
        movement = explorer.move_queue.get()

        right_front_obstacle = round(sensor_data["RightFront"] / 10)
        right_back_obstacle = round(sensor_data["RightBack"] / 10)

        # Display message
        if movement == '5':
            log_movement = 'right'
            right_wall_counter = 0

        elif movement == '4':
            # get_image(log_string, explorer, arduino_conn)
            log_movement = 'left'
            right_wall_counter = 0
            front_left_obstacle = round(sensor_data["FrontLeft"]/10)
            front_mid_obstacle = round(sensor_data["FrontCenter"]/10)
            front_right_obstacle = round(sensor_data["FrontRight"]/10)

            if front_left_obstacle < 2 and front_right_obstacle < 2 and front_mid_obstacle < 2:
                print(log_string + text_color.WARNING + 'Recalibrating corner' + text_color.ENDC)

                # Get sensor data
                send_param = "{\"dest\": \"arduino\", \"param\": \"12\"}"

                pc_conn.to_send_queue.put(send_param.encode())
                pc_conn.have_recv_queue.get()
                print(log_string + text_color.OKGREEN + 'Recalibrate corner done' + text_color.ENDC)

            elif (right_front_obstacle < 2 and right_back_obstacle < 2) and \
                    (front_left_obstacle < 2 or front_right_obstacle < 2 or front_mid_obstacle < 2):
                print(log_string + text_color.WARNING + 'Recalibrating right wall' + text_color.ENDC)

                # Calibrate right
                send_param = "{\"dest\": \"arduino\",\"param\": \"11\"}"

                pc_conn.to_send_queue.put(send_param.encode())
                pc_conn.have_recv_queue.get()
                right_wall_counter = 0
                print(log_string + text_color.OKGREEN + 'Recalibrate right wall done' + text_color.ENDC)
        else:
            log_movement = 'forward'
            right_wall_counter += 1

        print(log_string + text_color.BOLD + 'Moving {}'.format(log_movement) + text_color.ENDC)

        # Convert explored map into hex
        hex_exp_map = explorer.convert_map_to_hex(explorer.explored_map)
        hex_real_map = explorer.convert_map_to_hex(explorer.real_map)

        packet = "{\"dest\": \"bt\",  \
                   \"explored\": \"" + hex_exp_map + "\",  \
                   \"obstacle\": \"" + hex_real_map + "\",  \
                   \"movement\": \"" + log_movement[0] + "\",  \
                   \"direction\": \"" + explorer.direction + "\"}"

        pc_conn.send_channel(packet.encode())
        pc_conn.recv_channel()
        print(log_string + text_color.OKGREEN + 'Packet sent' + text_color.ENDC)

        if right_wall_counter >= 3 and (right_front_obstacle < 2 and right_back_obstacle < 2):
            print(log_string + text_color.WARNING + 'Recalibrating right wall' + text_color.ENDC)

            # Calibrate right
            send_param = "{\"dest\": \"arduino\",\"param\": \"11\"}"

            pc_conn.send_channel(send_param.encode())
            pc_conn.recv_channel()
            right_wall_counter = 0
            print(log_string + text_color.OKGREEN + 'Recalibrate right wall done' + text_color.ENDC)

        # Get sensor data
        send_param = "{\"dest\": \"arduino\", \"param\": \"" + movement + "\"}"

        pc_conn.send_channel(send_param.encode())
        pc_conn.recv_channel()

    print(log_string + text_color.OKGREEN + 'Explore completed' + text_color.ENDC)

    # Send empty packet to tell PC that stream has stopped
    # server_stream.queue.put('')

    # Convert real map to hex
    hex_real_map = explorer.convert_map_to_hex(explorer.real_map)
    hex_exp_map = explorer.convert_map_to_hex(explorer.explored_map)

    packet = "{\"dest\": \"bt\", \"obstacle\": \"" + hex_real_map + "\", \"explored\": \"" + hex_exp_map + "\"}"

    pc_conn.send_channel(packet.encode())
    pc_conn.recv_channel()

    # # Move to initial start
    # while not explorer.check_start():
    #
    #     # Get sensor data
    #     send_param = "{\"dest\": \"arduino\",\"param\": \"2\"}"
    #
    #     pc_conn.to_send_queue.put(send_param.encode())
    #     pc_conn.have_recv_queue.get()
    #
    #     sensor_data = pc_conn.have_recv_queue.get()
    #     sensor_data = sensor_data.decode().strip()
    #     sensor_data = json.loads(sensor_data)
    #
    #     # Actually move to new start position
    #     explorer.navigate_to_point(log_string, text_color, sensor_data, explorer.start)
    #     movement = explorer.move_queue.get()
    #
    #     send_param = "{\"dest\": \"arduino\",\"param\": \"" + movement + "\" }"
    #     pc_conn.to_send_queue.put(send_param.encode())
    #     pc_conn.have_recv_queue.get()

    # Save real map once done exploring
    explorer.save_map(hex_real_map)

    pc_conn.send_channel('end'.encode())
    pc_conn.recv_channel()

    return explorer


def get_image(log_string, explorer, arduino_conn):
    start_pos = explorer.current_pos
    start_dir = explorer.direction

    # while True:
    #     send_param = b'2'
    #     arduino_conn.to_send_queue.put(send_param)
    #     sensor_data = arduino_conn.have_recv_queue.get()
    #
    #     sensor_data = json.loads(sensor_data.decode().strip())
    #
    #     # Get the data
    #     front_left_obstacle = round(sensor_data["FrontLeft"]) / 10
    #     front_mid_obstacle = round(sensor_data["FrontCenter"]) / 10
    #     front_right_obstacle = round(sensor_data["FrontRight"]) / 10
    #     mid_left_obstacle = round(sensor_data["LeftSide"]) / 10
    #     right_front_obstacle = round(sensor_data["RightFront"]) / 10
    #     right_back_obstacle = round(sensor_data["RightBack"]) / 10
    #
    #     # Camera facing right
    #     # Turn left
    #     arduino_conn.to_send_queue.put(b'4')
    #     arduino_conn.have_recv_queue.get()
    #
    #     # Insert image recog code here
    #     # TODO: This is a placeholder!
    #     captured = ImageRecognition(text_color)
    #
    #     if captured:
    #         explorer.navigate_to_point(log_string, text_color, arduino_conn, start_pos)
    #         break
    #
    #     else:
    #         # If no obstacle on right
    #         if right_front_obstacle > 2 or right_back_obstacle > 2:
    #             arduino_conn.to_send_queue.put(b'5')
    #             arduino_conn.have_recv_queue.get()
    #
    #         # If front has obstacle
    #         elif front_left_obstacle < 2 or front_mid_obstacle < 2 or front_right_obstacle < 2:
    #             # Turn left
    #             arduino_conn.to_send_queue.put(b'4')
    #             arduino_conn.have_recv_queue.get()
    #
    #         else:
    #             # Advance
    #             arduino_conn.to_send_queue.put(b'3')
    #             arduino_conn.have_recv_queue.get()

    while not explorer.set_direction(start_dir):
        continue


def move_to_point(explorer, point):

    movement = []

    # Comparing x axis
    if explorer.current_pos[4][0] != point[0]:
        more = explorer.current_pos[4][0] - point[0]

        # Turn left if more
        if more > 0:
            movement.append("4")
            movement.append("3")

        # Turn right if less
        else:
            movement.append("5")
            movement.append("3")

    # Comparing y axis
    elif explorer.current_pos[4][1] != point[1]:
        more = explorer.current_pos[4][1] - point[1]

        # Move forward if more
        if more > 0:
            movement.append("3")

        # Move backward if less
        else:
            movement.append("6")

    return movement


if __name__ == "__main__":
    import platform
    try:
        main(platform.system())
        # main('Windows')
    except KeyboardInterrupt:
        os.system('pkill -9 python')

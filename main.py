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
    # Initialise variables here
    explorer = None
    
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
            mode = bt_conn.have_recv_queue.get()

            mode = mode.decode()

            # 4 modes to accommodate for: Explore, Image Recognition, Shortest Path, Manual and Disconnect
            if mode in ['beginExplore', 'imageRecognition', 'beginFastest', 'manual', 'disconnect']:

                # Send ack to Android device
                bt_conn.to_send_queue.put(('{} acknowledged'.format(mode)).encode())

                # Display on screen the mode getting executed
                print(log_string + text_color.OKGREEN + '{} Mode Initiated'.format(mode) + text_color.ENDC)

                if mode == 'beginExplore':
                    server_conn.to_send_queue.put(mode.encode())
                    robo_init(log_string, arduino_conn, bt_conn)

                    while True:
                        feedback = server_conn.have_recv_queue.get()
                        feedback = json.loads(feedback.decode())

                        if feedback['dest'] == 'arduino':
                            param = feedback['param']
                            arduino_conn.to_send_queue.put(param.encode())
                            msg = arduino_conn.have_recv_queue.get()
                            server_conn.have_recv_queue.put(msg)

                        elif feedback['dest'] == 'bt':
                            del feedback['dest']
                            feedback = str(feedback)
                            bt_conn.to_send_queue.put(feedback.encode())

                elif mode == 'Image Recognition':
                    print(mode)

                elif mode == 'beginFastest':
                    waypt = bt_conn.have_recv_queue.get()
                    server_conn.to_send_queue.put(waypt)
                    path = server_conn.have_recv_queue.get()
                    path = json.loads(path.decode())
                    for ele in path:
                        arduino_conn.to_send_queue.put(ele)

                elif mode == 'manual':
                    server_conn.to_send_queue.put('manual'.encode())
                    while True:
                        msg = bt_conn.have_recv_queue.get()
                        server_conn.to_send_queue.put(msg)
                        msg = msg.decode()
                        if msg == 'end':
                            break
                        movement = server_conn.have_recv_queue.get()
                        arduino_conn.to_send_queue.put(movement)
                        arduino_conn.have_recv_queue.get()

                elif mode == 'disconnect':
                    # Send message to PC and Arduino to tell them to disconnect
                    server_conn.to_send_queue.put('Disconnect'.encode())
                    arduino_conn.to_send_queue.put('Disconnect'.encode())

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
                bt_conn.to_send_queue.put('Send valid argument'.encode())

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

    try:
        while True:

            # Receive data from Raspberry Pi
            # TODO: Rasp Pi array here!
            data = pc_conn.have_recv_queue.get()

            data = data.decode()

            # 4 modes to accommodate for: Explore, Image Recognition, Shortest Path, Manual and Disconnect
            if data in ['beginExplore', 'imageRecognition', 'beginFastest', 'manual', 'disconnect']:

                # Send ack to Raspberry Pi
                # TODO: Rasp Pi array here!
                pc_conn.to_send_queue.put(('{} acknowledged'.format(data)).encode())

                # Display on screen the mode getting executed
                print(log_string + text_color.OKGREEN + '{} mode initiated'.format(data) + text_color.ENDC)

                if data == 'beginExplore':
                    explorer = explore(log_string, pc_conn)

                elif data == 'imageRecognition':
                    pass

                elif data == 'beginFastest':
                    waypt = pc_conn.have_recv_queue.get()
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

                    send_param = str({
                        "dest": "arduino",
                        "param": path
                    })
                    pc_conn.to_send_queue.put(send_param.encode())

                elif data == 'manual':
                    while True:
                        movement = pc_conn.have_recv_queue.get()

                        movement = movement.decode()

                        if movement == 'tl':
                            print(log_string + text_color.BOLD + 'Turn left' + text_color.ENDC)
                            pc_conn.to_send_queue.put(b'4')

                        elif movement == 'f':
                            print(log_string + text_color.BOLD + 'Move forward' + text_color.ENDC)
                            pc_conn.to_send_queue.put(b'3')

                        elif movement == 'tr':
                            print(log_string + text_color.BOLD + 'Turn right' + text_color.ENDC)
                            pc_conn.to_send_queue.put(b'5')

                        elif movement == 'r':
                            print(log_string + text_color.BOLD + 'Move backwards' + text_color.ENDC)
                            pc_conn.to_send_queue.put(b'6')

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
                pc_conn.to_send_queue.put('Send valid argument'.encode())

    except KeyboardInterrupt:
        os.system('pkill -9 python')


# This init is done assuming the robot does not start in a "room" in the corner
def robo_init(log_string, arduino_conn, bt_conn):
    """
    Function to init robot
    :param arduino_conn: Serial
            Serial class containing connection to Arduino
    :param bt_conn: Socket
            Socket containing connection to tablet0
    :return:
    """
    print(log_string + text_color.WARNING + 'Initialising' + text_color.ENDC)
    bt_conn.to_send_queue.put('Initialising'.encode())
    arduino_conn.to_send_queue.put(b'2')

    # Get feedback from Arduino
    feedback = arduino_conn.have_recv_queue.get()

    sensor_data = json.loads(feedback.decode().strip())

    # Get the data
    front_left_obstacle = round(sensor_data["FrontLeft"]) / 10
    front_mid_obstacle = round(sensor_data["FrontCenter"]) / 10
    front_right_obstacle = round(sensor_data["FrontRight"]) / 10
    right_front_obstacle = round(sensor_data["RightFront"]) / 10
    right_back_obstacle = round(sensor_data["RightBack"]) / 10

    # While there is no obstacle on the right
    while right_front_obstacle > 1 and right_back_obstacle > 1:

        # If there is no obstacle on the right, tell Arduino to turn right
        arduino_conn.to_send_queue.put(b'5')

        packet = str({
            "dest": "bt",
            "movement": "r",
            "direction": Direction.N
        })

        bt_conn.to_send_queue.put(packet.encode())

        # Refresh variables in freedback
        _ = arduino_conn.have_recv_queue.get()

        arduino_conn.to_send_queue.put(b'2')

        sensor_data = arduino_conn.have_recv_queue.get()
        sensor_data = json.loads(sensor_data.decode().strip())

        # Get the data
        front_left_obstacle = round(sensor_data["FrontLeft"]) / 10
        front_mid_obstacle = round(sensor_data["FrontCenter"]) / 10
        front_right_obstacle = round(sensor_data["FrontRight"]) / 10
        right_front_obstacle = round(sensor_data["RightFront"]) / 10
        right_back_obstacle = round(sensor_data["RightBack"]) / 10

    # If robot is facing corner, turn left
    if (front_left_obstacle <= 1 or front_mid_obstacle <= 1 or front_right_obstacle <= 1) and \
            right_front_obstacle <= 1 and right_back_obstacle <= 1:
        arduino_conn.to_send_queue.put(b'4')
        arduino_conn.have_recv_queue.get()
        packet = str({
            "dest": "bt",
            "movement": 'l',
            "direction": Direction.N
        })

    arduino_conn.to_send_queue.put(b'11')
    arduino_conn.have_recv_queue.get()
    bt_conn.to_send_queue.put('Initialising done'.encode())
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

    # While map is not complete
    while not explorer.is_map_complete():

        right_wall_counter = 0

        # While round is not complete
        while not explorer.check_round_complete():

            print(log_string + text_color.WARNING + 'Round not completed' + text_color.ENDC)

            print(log_string + text_color.BOLD + 'Getting sensor data' + text_color.ENDC)

            # Get sensor data
            send_param = str({
                'dest': "arduino",
                'param': b'2'
            })

            pc_conn.to_send_queue.put(send_param.encode())
            sensor_data = pc_conn.have_recv_queue.get()

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
                right_wall_counter = 0

            elif movement == b'4':
                # get_image(log_string, explorer, arduino_conn)
                log_movement = b'left'
                right_wall_counter = 0
                front_left_obstacle = round(sensor_data["FrontLeft"]) / 10
                front_mid_obstacle = round(sensor_data["FrontCenter"]) / 10
                front_right_obstacle = round(sensor_data["FrontRight"]) / 10

                if front_left_obstacle < 2 and front_right_obstacle < 2 and front_mid_obstacle < 2:
                    print(log_string + text_color.WARNING + 'Recalibrating corner' + text_color.ENDC)

                    # Get sensor data
                    send_param = str({
                        'dest': "arduino",
                        'param': b'10'
                    })

                    pc_conn.to_send_queue.put(send_param.encode())
                    print(log_string + text_color.OKGREEN + 'Recalibrate corner done' + text_color.ENDC)
            else:
                log_movement = 'forward'
                right_wall_counter += 1

            print(log_string + text_color.BOLD + 'Moving {}'.format(log_movement) + text_color.ENDC)

            # Get sensor data
            send_param = str({
                'dest': "arduino",
                'param': movement
            })

            pc_conn.to_send_queue.put(send_param.encode())

            # Convert explored map into hex
            hex_exp_map = explorer.convert_map_to_hex(explorer.explored_map)
            hex_real_map = explorer.convert_map_to_hex(explorer.real_map)

            packet = str({
                "dest": "bt",
                "explored": hex_exp_map,
                "obstacle": hex_real_map,
                "movement": log_movement[0],
                "direction": explorer.direction
            })

            pc_conn.to_send_queue.put(packet.encode())
            print(log_string + text_color.OKGREEN + 'Packet sent' + text_color.ENDC)

            # TODO: Send image to PC
            # server_stream.queue.put(stream_byte)
            # print(log_string + text_color.OKBLUE + 'Stream data sent to PC' + text_color.ENDC)

            if right_wall_counter == 5:
                print(log_string + text_color.WARNING + 'Recalibrating right wall' + text_color.ENDC)

                # Get sensor data
                send_param = str({
                    'dest': "arduino",
                    'param': b'2'
                })

                pc_conn.to_send_queue.put(send_param.encode())
                pc_conn.have_recv_queue.get()
                right_wall_counter = 0
                print(log_string + text_color.OKGREEN + 'Recalibrate right wall done' + text_color.ENDC)

        # If round is complete, shift starting position
        explorer.update_start(3, 3)
        print(log_string + text_color.OKGREEN + 'Round completed' + text_color.ENDC)
        print(log_string + text_color.BOLD + 'Updated start by 3' + text_color.ENDC)

        while not explorer.check_start() and not explorer.is_map_complete():

            # Get sensor data
            send_param = str({
                'dest': "arduino",
                'param': b'2'
            })

            pc_conn.to_send_queue.put(send_param.encode())
            sensor_data = pc_conn.have_recv_queue.get()

            sensor_data = sensor_data.decode().strip()

            sensor_data = json.loads(sensor_data)

            # Actually move to new start position
            explorer.navigate_to_point(log_string, text_color, sensor_data, explorer.start)

            movement = explorer.move_queue.get()

            send_param = str({
                'dest': "arduino",
                'param': movement
            })

            pc_conn.to_send_queue.put(send_param.encode())

            if movement == b'5':
                log_movement = 'right'

            elif movement == b'4':
                log_movement = 'left'

            else:
                log_movement = 'forward'

            send_param = str({
                'dest': 'bt',
                'movement': log_movement[0],
                'direction': explorer.direction
            })

            pc_conn.to_send_queue.put(send_param.encode())

    print(log_string + text_color.OKGREEN + 'Explore completed' + text_color.ENDC)

    # Send empty packet to tell PC that stream has stopped
    # server_stream.queue.put('')

    # Convert real map to hex
    hex_real_map = explorer.convert_map_to_hex(explorer.real_map)
    hex_exp_map = explorer.convert_map_to_hex(explorer.explored_map)

    packet = str({
        "dest": "bt",
        "obstacle": hex_real_map,
        "explored": hex_exp_map
    })

    pc_conn.to_send_queue.put(packet.encode())

    # Move to initial start
    while not explorer.check_start():
        # Get sensor data
        send_param = str({
            'dest': "arduino",
            'param': b'2'
        })

        pc_conn.to_send_queue.put(send_param.encode())
        sensor_data = pc_conn.have_recv_queue.get()

        sensor_data = sensor_data.decode().strip()

        sensor_data = json.loads(sensor_data)

        # Actually move to new start position
        explorer.navigate_to_point(log_string, text_color, sensor_data, explorer.start)

        movement = explorer.move_queue.get()

        send_param = str({
            'dest': "arduino",
            'param': movement
        })
        pc_conn.to_send_queue.put(send_param.encode())

    # Save real map once done exploring
    explorer.save_map(hex_real_map)

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
            movement.append(b'4')
            movement.append(b'3')

        # Turn right if less
        else:
            movement.append(b'5')
            movement.append(b'3')

    # Comparing y axis
    elif explorer.current_pos[4][1] != point[1]:
        more = explorer.current_pos[4][1] - point[1]

        # Move forward if more
        if more > 0:
            movement.append(b'3')

        # Move backward if less
        else:
            movement.append(b'6')

    return movement


if __name__ == "__main__":
    import platform
    try:
        # main(platform.system())
        main('Windows')
    except KeyboardInterrupt:
        os.system('pkill -9 python')

# Import written classes
from RPi.server import Server
from RPi.arduino import Arduino
from RPi.client import Client
from Algo.explore import Explore
from Algo.image_recognition import ImageRecognition
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
import threading


class Main:
    def __init__(self, sys_type):
        self.arduino_conn_thread = None
        self.server_conn_thread = None
        self.bt_conn_thread = None
        self.pc_conn_thread = None

        self.arduino_conn = None
        self.server_conn = None
        self.bt_conn = None
        self.pc_conn = None

        # added for image recognition
        self.camera = None
        self.image_recognition = None

        self.sys_type = sys_type
        self.rpi_ip = '192.168.17.17'
        self.rpi_mac_addr = 'B8:27:EB:52:AC:83'
        self.arduino_name = '/dev/ttyACM0'
        self.log_string = text_color.OKBLUE + "Main: " + text_color.ENDC

        self.explorer = None
        self.waypt_coord = None

    def start(self):
        """
        Main function of MDP Project, execute this file to start
        :param sys_type: String
                String containing System Type (Windows, Linux or Mac)
        :return:
        """

        # If running on Pi, run relevant threads
        if self.sys_type == 'Linux':
            self.rpi()

        # If running on own PC, run instance of algorithms
        elif self.sys_type == 'Windows' or self.sys_type == 'Darwin':
            self.pc()

        print(text_color.WARNING + 'End of program reached.' + text_color.ENDC)

    def pc(self):
        """
        Function to start running code on PC
        :param rpi_ip: String
                String containing IP address of Raspberry Pi
        :param log_string: String
                String containing format of log to be used
        :return:
        """
        # Create an instance of PC
        self.pc_conn = Client(self.rpi_ip, 7777, text_color)
        self.image_recognition = ImageRecognition()

        # Connect to Raspberry Pi
        self.pc_conn.connect()

        self.pc_conn_thread = threading.Thread(target=self.read_pc)
        self.pc_conn_thread.start()

    def rpi(self):
        """
        Function to start running code on Raspberry Pi
        :param rpi_ip: String
                String containing IP address of Raspberry Pi
        :param rpi_mac_addr: String
                String containing MAC address of Raspberry Pi
        :param arduino_name: String
                String containing Arduino device name
        :return:
        """
        from RPi.bluetooth import Bluetooth
        from RPi.camera import Camera

        self.camera = camera()

        # Connect to Arduino
        self.arduino_conn = Arduino(self.arduino_name, text_color)

        # Connect to PC
        self.server_conn = Server(self.rpi_ip, 7777, text_color)
        self.server_conn.listen()

        # Connect to Tablet
        self.bt_conn = Bluetooth(self.rpi_mac_addr, text_color)
        self.bt_conn.listen()

        self.arduino_conn_thread = threading.Thread(target=self.read_arduino)
        self.server_conn_thread = threading.Thread(target=self.read_server)
        self.bt_conn_thread = threading.Thread(target=self.read_bt)

        self.arduino_conn_thread.daemon = True
        self.server_conn_thread.daemon = True
        self.bt_conn_thread.daemon = True

        self.arduino_conn_thread.start()
        self.server_conn_thread.start()
        self.bt_conn_thread.start()

    def read_arduino(self):
        while True:
            msg = self.arduino_conn.recv()
            self.write_server(msg)

    def write_arduino(self, msg):
        time.sleep(0.5)
        self.arduino_conn.send(msg)

    def read_server(self):
        while True:
            feedback = self.server_conn.recv()
            self.write_server('ack'.encode())
            feedback = feedback.decode()
            if feedback == 'end':
                break
            feedback = json.loads(feedback)

            if feedback["dest"] == "arduino":
                param = feedback["param"]
                self.write_arduino(param.encode())

            elif feedback["dest"] == "bt":
                del feedback["dest"]
                feedback = str(feedback)
                self.write_bt(feedback.encode())

            # added for image recognition
            elif feedback["dest"] == "rpi":
                self.camera.capture()

            else:
                pass

    def write_server(self, msg):
        self.server_conn.send(msg)

    def read_bt(self):
        while True:
            msg = self.bt_conn.recv()
            self.process_bt_msg(msg.decode())

    def write_bt(self, msg):
        self.bt_conn.send(msg)

    def process_bt_msg(self, msg):

        # 4 modes to accommodate for: Explore, Image Recognition, Shortest Path, Manual and Disconnect
        if msg in ['init', 'beginExplore', 'imageRecognition', 'beginFastest', 'manual', 'disconnect']:

            # Display on screen the mode getting executed
            print(text_color.OKGREEN + '{} Mode Initiated'.format(msg) + text_color.ENDC)

            if msg == 'init':
                self.server_conn.send('init'.encode())
                self.robo_init()
                waypt = self.bt_conn.recv()
                self.write_server(waypt)
                packet = "{\"dest\": \"bt\",\"direction\": \"" + Direction.N + "\" }"
                self.write_bt(packet.encode())

            elif msg == 'beginExplore':
                self.write_server(msg.encode())
                self.read_server()

            elif msg == 'imageRecognition':

                # added for image recognition
                # send the images took by RPi
                self.server_conn.send_images()

                # receive the predicted result
                result = server_conn.recv()
                result = json.loads(result)
                
                # send the string to tablet for display
                self.write_bt(result.encode())


            elif msg == 'beginFastest':
                self.write_server(msg.encode())

            elif msg == 'manual':
                self.write_server('manual'.encode())
                while True:
                    msg = self.bt_conn.recv()
                    self.write_server(msg)
                    msg = msg.decode()
                    if msg == 'end':
                        print(text_color.OKGREEN + 'Explore ended' + text_color.ENDC)
                        break

            elif msg == 'disconnect':
                # Send message to PC and Arduino to tell them to disconnect
                self.write_server('Disconnect'.encode())
                self.write_arduino('Disconnect'.encode())

                # Disconnect from wifi and bluetooth connection
                self.server_conn.disconnect()
                self.arduino_conn.disconnect()
                self.bt_conn.disconnect()
                return

        else:
            # Display feedback so that user knows this condition is triggered
            print(text_color.FAIL +
                  'Invalid message {} received.'.format(msg)
                  + text_color.ENDC)

            # Add data into queue for sending to tablet
            self.write_bt('Send valid argument'.encode())

    def read_pc(self):
        while True:
            msg = self.pc_conn.recv()
            self.process_pc_msg(msg)

    def write_pc(self, msg):
        self.pc_conn.send(msg)

    def process_pc_msg(self, msg):
        flag = 0
        path = []

        data = msg.decode()

        # 4 modes to accommodate for: Explore, Image Recognition, Shortest Path, Manual and Disconnect
        if data in ['init', 'beginExplore', 'imageRecognition', 'beginFastest', 'manual', 'disconnect']:

            # Display on screen the mode getting executed
            print(self.log_string + text_color.OKGREEN + '{} mode initiated'.format(data) + text_color.ENDC)

            if data == 'init':
                waypt = self.pc_conn.recv()
                waypt = waypt.decode()

                waypt = json.loads(waypt)
                self.waypt_coord = [waypt['x'], waypt['y']]

            elif data == 'beginExplore':
                self.explorer = self.explore()
                start = [[2, 2], [2, 1], [2, 0], [1, 2], [1, 1], [1, 0], [0, 2], [0, 1], [0, 0]]
                start_point = Point(start[4][0], start[4][1])
                end_point = Point(self.waypt_coord[0], self.waypt_coord[1])
                for _ in range(2):
                    a_star = AStar(start[4], self.waypt_coord, self.explorer.real_map)
                    start_pt = AStar.Node(start_point, end_point, 0)
                    a_star.open_list.append(start_pt)

                    while not flag:
                        a_star_current = a_star.select_current()
                        flag = a_star.near_explore(a_star_current)

                    for node_path in a_star.path:
                        movements = self.move_to_point(self.explorer, node_path.point)
                        for ele in movements:
                            path.append(ele)

                    start = Point(self.explorer.current_pos[4][0], self.explorer.current_pos[4][1])
                    self.waypt_coord = Point(self.explorer.goal[4][0], self.explorer.goal[4][1])

            elif data == 'imageRecognition':
                
                # added for image recognition
                # receive images from the server
                pc_conn.recv_images()

                # load received images from designated directory
                images = image_recognition.load_images()

                # make prediction for each image received
                for image in images:
                    image_recognition.predict(image)

                # get the predicted signs' id
                result = image_recognition.get_predicted_ids()

                # send the required string to server
                pc_conn.send(result.encode())

            elif data == 'beginFastest':
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

                send_param = "{\"dest\": \"arduino\",\"param\": \"14\" }"
                self.write_pc(send_param.encode())

                send_param = "{\"dest\": \"arduino\",\"param\": \"" + path_string + "\" }"
                self.write_pc(send_param.encode())

            elif data == 'manual':
                while True:
                    movement = self.pc_conn.recv()

                    movement = movement.decode()

                    if movement == 'tl':
                        print(self.log_string + text_color.BOLD + 'Turn left' + text_color.ENDC)
                        packet = "{\"dest\": \"arduino\", \"param:\"A1\"}"

                    elif movement == 'f':
                        print(self.log_string + text_color.BOLD + 'Move forward' + text_color.ENDC)
                        packet = "{\"dest\": \"arduino\", \"param:\"W1\"}"

                    elif movement == 'tr':
                        print(self.log_string + text_color.BOLD + 'Turn right' + text_color.ENDC)
                        packet = "{\"dest\": \"arduino\", \"param:\"D1\"}"

                    elif movement == 'r':
                        print(self.log_string + text_color.BOLD + 'Move backwards' + text_color.ENDC)
                        packet = "{\"dest\": \"arduino\", \"param:\"S1\"}"

                    elif movement == 'end':
                        break

                    else:
                        packet = "{\"dest\": \"nothing\"}"
                        print(self.log_string + text_color.FAIL + 'Command unrecognised' + text_color.ENDC)

                    self.write_pc(packet.encode())

                print(self.log_string + text_color.WARNING + 'Manual mode terminated' + text_color.ENDC)

            elif data == 'disconnect':
                # Disconnect from Raspberry Pi
                self.pc_conn.disconnect()
                return

        else:
            # Display feedback so that user knows this condition is triggered
            print(self.log_string + text_color.FAIL + 'Invalid argument "{}" received.'.format(data) + text_color.ENDC)

            # Add data into queue for sending to Raspberry Pi
            # Failsafe condition
            self.write_pc('Send valid argument'.encode())

    def robo_init(self):
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
        print(self.log_string + text_color.WARNING + 'Initialising' + text_color.ENDC)
        self.write_arduino(b'I1')
        print(self.log_string + text_color.OKGREEN + 'Initialising done' + text_color.ENDC)

    def explore(self):
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

        true_start = [[2, 2], [2, 1], [2, 0], [1, 2], [1, 1], [1, 0], [0, 2], [0, 1], [0, 0]]
        start = [[2, 2], [2, 1], [2, 0], [1, 2], [1, 1], [1, 0], [0, 2], [0, 1], [0, 0]]

        print(self.log_string + text_color.OKGREEN + 'Explore started' + text_color.ENDC)

        right_wall_counter = 0
        i = 0

        print(self.log_string + text_color.BOLD + 'Getting sensor data' + text_color.ENDC)

        # Get sensor data
        send_param = "{\"dest\":\"arduino\",\"param\":\"E1\"}"
        self.write_pc(send_param.encode())
        self.pc_conn.recv()

        while not explorer.is_round_complete(start):

            print("Current position:\n", explorer.current_pos)
            print("Direction:\n", explorer.direction)
            print("True start:\n", explorer.true_start)
            print("Explored map:\n", explorer.explored_map)
            print("Obstacle map:\n", explorer.real_map)

            print(self.log_string + text_color.WARNING + 'Round not completed' + text_color.ENDC)

            sensor_data = self.pc_conn.recv()
            sensor_data = sensor_data.decode().strip()
            sensor_data = json.loads(sensor_data)

            explorer.sensor_data_queue.put(sensor_data)
            print(self.log_string + text_color.OKGREEN + 'Sensor data received' + text_color.ENDC)

            # Get next movement
            movement = explorer.move_queue.get()
            right_front_obstacle = round(sensor_data["RightFront"] / 10)
            right_back_obstacle = round(sensor_data["RightBack"] / 10)

            # Display message
            if movement == 'D1':
                log_movement = 'right'
                right_wall_counter = 0

            elif movement == 'A1':
                # get_image(log_string, explorer, arduino_conn)
                log_movement = 'left'
                front_left_obstacle = round(sensor_data["FrontLeft"]/10)
                front_mid_obstacle = round(sensor_data["FrontCenter"]/10)
                front_right_obstacle = round(sensor_data["FrontRight"]/10)

                if (front_left_obstacle < 2 and front_right_obstacle < 2 and front_mid_obstacle < 2) and \
                    (right_back_obstacle < 2 and right_front_obstacle < 2):
                    print(self.log_string + text_color.WARNING + 'Recalibrating corner' + text_color.ENDC)

                    # Get sensor data
                    send_param = "{\"dest\": \"arduino\", \"param\": \"N1\"}"

                    self.pc_conn.send(send_param.encode())
                    self.pc_conn.recv()
                    time.sleep(0.5)
                    self.pc_conn.recv()
                    print(self.log_string + text_color.OKGREEN + 'Recalibrate corner done' + text_color.ENDC)

                elif (front_left_obstacle < 2 and front_right_obstacle < 2) or \
                     (front_mid_obstacle < 2 and front_right_obstacle < 2) or \
                     (front_left_obstacle < 2 and front_mid_obstacle < 2):
                    print(self.log_string + text_color.WARNING + 'Recalibrating front' + text_color.ENDC)

                    # Get sensor data
                    send_param = "{\"dest\": \"arduino\", \"param\": \"F1\"}"

                    self.pc_conn.send(send_param.encode())
                    self.pc_conn.recv()
                    time.sleep(0.5)
                    self.pc_conn.recv()
                    print(self.log_string + text_color.OKGREEN + 'Recalibrate front done' + text_color.ENDC)

                right_wall_counter = 0

            else:
                log_movement = 'forward'
                right_wall_counter += 1
                explorer.round = 1

                if (right_wall_counter % 4 == 0) and (right_front_obstacle < 2 and right_back_obstacle < 2):
                    print(self.log_string + text_color.WARNING + 'Recalibrating right wall' + text_color.ENDC)

                    # Calibrate right
                    send_param = "{\"dest\": \"arduino\",\"param\": \"R1\"}"

                    self.pc_conn.send(send_param.encode())
                    self.pc_conn.recv()
                    time.sleep(0.5)
                    self.pc_conn.recv()

                    right_wall_counter = 0
                    print(self.log_string + text_color.OKGREEN + 'Recalibrate right wall done' + text_color.ENDC)

            print(self.log_string + text_color.BOLD + 'Moving {}'.format(log_movement) + text_color.ENDC)

            # Convert explored map into hex
            hex_exp_map = explorer.convert_map_to_hex(explorer.explored_map)
            hex_real_map = explorer.convert_map_to_hex(explorer.real_map)

            packet = "{\"dest\": \"bt\",  \
                       \"explored\": \"" + hex_exp_map + "\",  \
                       \"obstacle\": \"" + hex_real_map + "\",  \
                       \"movement\": \"" + log_movement[0] + "\",  \
                       \"direction\": \"" + explorer.direction + "\"}"

            self.write_pc(packet.encode())
            self.pc_conn.recv()
            print(self.log_string + text_color.OKGREEN + 'Packet sent' + text_color.ENDC)

            # Get sensor data
            send_param = "{\"dest\": \"arduino\", \"param\": \"" + movement + "\"}"

            self.pc_conn.send(send_param.encode())
            self.pc_conn.recv()

        print(self.log_string + text_color.OKGREEN + 'Explore completed' + text_color.ENDC)

        # Convert real map to hex
        hex_real_map = explorer.convert_map_to_hex(explorer.real_map)
        hex_exp_map = explorer.convert_map_to_hex(explorer.explored_map)

        packet = "{\"dest\": \"bt\", \"obstacle\": \"" + hex_real_map + "\", \"explored\": \"" + hex_exp_map + "\"}"

        self.pc_conn.send(packet.encode())
        self.pc_conn.recv()

        # Save real map once done exploring
        explorer.save_map(hex_real_map)

        self.pc_conn.send('end'.encode())
        self.pc_conn.recv()

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

    def move_to_point(self, explorer, point):

        movement = []

        # Comparing x axis
        if explorer.current_pos[4][0] != point[0]:
            more = explorer.current_pos[4][0] - point[0]

            # Turn left if more
            if more > 0:
                movement.append("A1")
                movement.append("W1")

            # Turn right if less
            else:
                movement.append("D1")
                movement.append("W1")

        # Comparing y axis
        elif explorer.current_pos[4][1] != point[1]:
            more = explorer.current_pos[4][1] - point[1]

            # Move forward if more
            if more > 0:
                movement.append("W1")

            # Move backward if less
            else:
                movement.append("S1")

        return movement

    def keep_main_alive(self):
        while True:
            print(self.log_string + text_color.OKGREEN + "Program is alive" + text_color.ENDC)
            time.sleep(10)

    def get_index(self):
        for i in range(len(self.explorer.explored_map), 0, -1):
            for j in range(len(self.explorer.explored_map[0]), 0, -1):
                if self.explorer.explored_map[i][j] == 0:
                    return [i, j]


if __name__ == "__main__":
    import platform
    try:
        main = Main(platform.system())
        # main('Windows')
        main.start()
        main.keep_main_alive()
    except KeyboardInterrupt:
        print("Program ending")
        #os.system('pkill -9 python')

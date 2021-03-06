# Import written classes
from RPi.server import Server
from RPi.arduino import Arduino
from RPi.client import Client
from Algo.explore import Explore
from Algo.img_recognition import ImageRecognition
# from Algo.a_star import AStar
# from Algo.shortest_path import ShortestPath
from Algo.fastest_path import *
from config.text_color import TextColor as text_color
from config.direction import Direction
from config.round import normal_round

# Import libraries
import json
import time
import os
import threading


class Main:
    def __init__(self, sys_type):
        self.arduino_conn_thread = None
        self.server_cmd_conn_thread = None
        self.server_img_conn_thread = None
        self.bt_conn_thread = None

        self.arduino_conn = None
        self.server_cmd_conn = None
        self.server_img_conn = None
        self.bt_conn = None

        self.pc_cmd_conn_thread = None
        self.pc_img_conn_thread = None

        self.pc_cmd_conn = None
        self.pc_img_conn = None

        # added for image recognition
        self.camera = None
        self.image_recognition = None

        self.sys_type = sys_type
        self.rpi_ip = '192.168.17.17'
        self.rpi_mac_addr = 'B8:27:EB:52:AC:83'
        self.arduino_name = '/dev/ttyACM0'
        self.log_string = text_color.OKBLUE + "Main: " + text_color.ENDC

        self.explorer = None
        self.waypt_coord = []
        self.path_string = ''
        self.capture_flag = False

    def start(self, param=None):
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
            if param == 'cmd':
                self.pc_cmd()
            else:
                self.pc_img()

        print(text_color.WARNING + 'End of program reached.' + text_color.ENDC)

    def pc_cmd(self):
        """
        Function to start running code on PC
        :param rpi_ip: String
                String containing IP address of Raspberry Pi
        :param log_string: String
                String containing format of log to be used
        :return:
        """
        # Create an instance of PC
        self.pc_cmd_conn = Client(self.rpi_ip, 7777, text_color)

        # Connect to Raspberry Pi
        self.pc_cmd_conn.connect()

        self.pc_cmd_conn_thread = threading.Thread(target=self.read_cmd_pc)
        self.pc_cmd_conn_thread.start()

    def pc_img(self):
        """
        Function to start running code on PC
        :param rpi_ip: String
                String containing IP address of Raspberry Pi
        :param log_string: String
                String containing format of log to be used
        :return:
        """
        # Create an instance of PC
        self.pc_img_conn = Client(self.rpi_ip, 8888, text_color)
        self.image_recognition = ImageRecognition()

        # Connect to Raspberry Pi
        self.pc_img_conn.connect()

        self.pc_img_conn_thread = threading.Thread(target=self.read_img_pc)
        self.pc_img_conn_thread.start()

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

        self.camera = Camera()

        # Connect to Arduino
        self.arduino_conn = Arduino(self.arduino_name, text_color)

        # Connect to PC
        self.server_cmd_conn = Server(self.rpi_ip, 7777, text_color)
        self.server_img_conn = Server(self.rpi_ip, 8888, text_color)
        self.server_cmd_conn.listen()
        self.server_img_conn.listen()

        # Connect to Tablet
        self.bt_conn = Bluetooth(self.rpi_mac_addr, text_color)
        self.bt_conn.listen()

        self.arduino_conn_thread = threading.Thread(target=self.read_arduino)
        self.server_cmd_conn_thread = threading.Thread(target=self.read_cmd_server)
        self.bt_conn_thread = threading.Thread(target=self.read_bt)

        self.arduino_conn_thread.daemon = True
        self.server_cmd_conn_thread.daemon = True
        # self.server_img_conn_thread.daemon = True
        self.bt_conn_thread.daemon = True

        self.arduino_conn_thread.start()
        self.server_cmd_conn_thread.start()
        # self.server_img_conn_thread.start()
        self.bt_conn_thread.start()

    def read_arduino(self):
        while True:
            msg = self.arduino_conn.recv()
            self.write_cmd_server(msg)

    def write_arduino(self, msg):
        time.sleep(0.5)
        self.arduino_conn.send(msg)

    def read_cmd_server(self):

        count = 0 
        while True:
            feedback = self.server_cmd_conn.recv()
            self.write_cmd_server('ack'.encode())

            feedback = feedback.decode()

            if feedback == 'end':
                break
            feedback = json.loads(feedback)

            if feedback["dest"] == "arduino":
                param = feedback["param"]

                if count % 2 == 0:
                    self.server_img_conn.send("C".encode())
                    self.camera.capture()
                    self.write_img_server(self.camera.counter)

                # count += 1
                self.write_arduino(param.encode())

            elif feedback["dest"] == "bt":
                del feedback["dest"]
                feedback = str(feedback)
                self.write_bt(feedback.encode())

            elif feedback["dest"] == "rpi":
                param = feedback["param"]

                if param == "S":
                    self.server_img_conn.send("S".encode())
                    img_id = self.server_img_conn.recv()
                    self.write_cmd_server(img_id)

    def write_cmd_server(self, msg):
        self.server_cmd_conn.send(msg)

    def write_img_server(self, msg):
        self.server_img_conn.send_image(msg)

    def read_bt(self):
        while True:
            msg = self.bt_conn.recv()
            self.process_bt_msg(msg.decode())
    
    def write_bt(self, msg):
        self.bt_conn.send(msg)

    def process_bt_msg(self, msg):

        # 4 modes to accommodate for: Explore, Image Recognition, Shortest Path, Manual and Disconnect
        if msg in ['init', 'beginExplore', 'beginFastest', 'manual', 'disconnect']:

            # Display on screen the mode getting executed
            print(text_color.OKGREEN + '{} Mode Initiated'.format(msg) + text_color.ENDC)

            if msg == 'init':
                self.server_cmd_conn.send('init'.encode())
                self.robo_init()
                waypt = self.bt_conn.recv()
                self.write_cmd_server(waypt)
                packet = "{\"dest\": \"bt\",\"direction\": \"" + Direction.N + "\" }"
                self.write_bt(packet.encode())

            elif msg == 'beginExplore':
                self.write_cmd_server(msg.encode())
                self.read_cmd_server()

            elif msg == 'beginFastest':
                self.write_cmd_server(msg.encode())

            elif msg == 'manual':
                self.write_cmd_server('manual'.encode())
                while True:
                    msg = self.bt_conn.recv()
                    self.write_cmd_server(msg)
                    msg = msg.decode()
                    if msg == 'end':
                        print(text_color.OKGREEN + 'Explore ended' + text_color.ENDC)
                        break

            elif msg == 'disconnect':
                # Send message to PC and Arduino to tell them to disconnect
                self.write_cmd_server('Disconnect'.encode())
                self.write_arduino('Disconnect'.encode())

                # Disconnect from wifi and bluetooth connection
                self.server_cmd_conn.disconnect()
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

    def read_cmd_pc(self):
        while True:
            msg = self.pc_cmd_conn.recv()
            self.process_pc_msg(msg)

    def read_img_pc(self):
        while True:
            msg = self.pc_img_conn.recv()
            msg = msg.decode()

            if msg == "C":
                self.pc_img_conn.recv_image()
                self.process_img()
            if msg == "S":
                predicted_ids = self.image_recognition.get_predicted_ids()
                self.pc_img_conn.send(predicted_ids.encode())
        
    def write_cmd_pc(self, msg):
        self.pc_cmd_conn.send(msg)

    def write_img_pc(self, msg):
        self.pc_img_conn.send(msg)

    def process_img(self):

        img = self.image_recognition.load_image()
        self.image_recognition.predict(img)
        print("Processing Image!")

    def process_pc_msg(self, msg):

        data = msg.decode()

        # 4 modes to accommodate for: Explore, Image Recognition, Shortest Path, Manual and Disconnect
        if data in ['init', 'beginExplore', 'beginFastest', 'manual', 'disconnect']:

            # Display on screen the mode getting executed
            print(self.log_string + text_color.OKGREEN + '{} mode initiated'.format(data) + text_color.ENDC)

            if data == 'init':
                waypt = self.pc_cmd_conn.recv()
                waypt = waypt.decode()

                waypt = json.loads(waypt)
                self.waypt_coord.append(waypt['x'])
                self.waypt_coord.append(waypt['y'])

            elif data == 'beginExplore':
                initial_start = Point(1, 1)
                self.explorer = self.explore(initial_start)

            elif data == 'beginFastest':

                send_param = "{\"dest\": \"arduino\",\"param\": \"Z\" }"
                self.write_cmd_pc(send_param.encode())
                self.pc_cmd_conn.recv()

                send_param = "{\"dest\": \"arduino\",\"param\": \"" + self.path_string + "\" }"
                self.write_cmd_pc(send_param.encode())
                self.pc_cmd_conn.recv()

            elif data == 'manual':
                while True:
                    movement = self.pc_cmd_conn.recv()

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

                    self.write_cmd_pc(packet.encode())

                print(self.log_string + text_color.WARNING + 'Manual mode terminated' + text_color.ENDC)

            elif data == 'disconnect':
                # Disconnect from Raspberry Pi
                self.pc_cmd_conn.disconnect()
                return

        else:
            # Display feedback so that user knows this condition is triggered
            print(self.log_string + text_color.FAIL + 'Invalid argument "{}" received.'.format(data) + text_color.ENDC)

            # Add data into queue for sending to Raspberry Pi
            # Failsafe condition
            self.write_cmd_pc('Send valid argument'.encode())

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

    def explore(self, initial_start):
        """
        Function to run explore algorithm
        :param log_string: String
                Format of log
        :param pc_conn: Socket
                Socket containing connection between PC and RPi
        :return:
        """

        # Start an instance of Explore class
        self.explorer = Explore(initial_start, Direction, normal_round)

        print(self.log_string + text_color.OKGREEN + 'Explore started' + text_color.ENDC)

        right_wall_counter = 0
        flag = 0
        path = []

        print(self.log_string + text_color.BOLD + 'Getting sensor data' + text_color.ENDC)

        # Get sensor data
        send_param = "{\"dest\":\"arduino\",\"param\":\"E1\"}"
        self.write_cmd_pc(send_param.encode())
        self.pc_cmd_conn.recv()

        while not self.explorer.is_round_complete():

            print("Current position:\n", self.explorer.current_pos)
            # print("Direction:\n", explorer.direction)
            # print("True start:\n", explorer.true_start)
            # print("Explored map:\n", explorer.explored_map)
            # print("Obstacle map:\n", explorer.real_map)

            """
            Check the position of the robot and take images accordingly
            ([4][1] == 1) and ([4][1] == 18) implies its hugging along the x-axis
            ([4][0] == 1) and ([4][0] == 13) implies its hugging along the y-axis
            """

            print(self.log_string + text_color.WARNING + 'Round not completed' + text_color.ENDC)

            sensor_data = self.pc_cmd_conn.recv()
            print(sensor_data)
            sensor_data = sensor_data.decode().strip()
            sensor_data = json.loads(sensor_data)

            self.explorer.sensor_data_queue.put(sensor_data)
            print(self.log_string + text_color.OKGREEN + 'Sensor data received' + text_color.ENDC)

            # Get next movement
            movement = self.explorer.move_queue.get()
            right_front_obstacle = normal_round(sensor_data["RightFront"] / 10)
            right_back_obstacle = normal_round(sensor_data["RightBack"] / 10)

            # Display message
            if movement == 'D1':
                log_movement = 'right'
                right_wall_counter = 0

            elif movement == 'A1':
                # get_image(log_string, explorer, arduino_conn)
                log_movement = 'left'

                front_left_obstacle = normal_round(sensor_data["FrontLeft"]/10)
                front_mid_obstacle = normal_round(sensor_data["FrontCenter"]/10)
                front_right_obstacle = normal_round(sensor_data["FrontRight"]/10)

                # if any of the 2 front sensor has an object and both the sensors on the right has an object
                if ((front_left_obstacle < 2 and front_right_obstacle < 2) or
                    (front_mid_obstacle < 2 and front_right_obstacle < 2) or
                    (front_left_obstacle < 2 and front_mid_obstacle < 2)) and \
                    (right_back_obstacle < 2 and right_front_obstacle < 2):
                    print(self.log_string + text_color.WARNING + 'Recalibrating corner' + text_color.ENDC)

                    # Get sensor data
                    send_param = "{\"dest\": \"arduino\", \"param\": \"N1\"}"

                    self.pc_cmd_conn.send(send_param.encode())
                    self.pc_cmd_conn.recv()
                    time.sleep(0.5)
                    self.pc_cmd_conn.recv()
                    print(self.log_string + text_color.OKGREEN + 'Recalibrate corner done' + text_color.ENDC)

                elif (front_left_obstacle < 2 and front_right_obstacle < 2) or \
                     (front_mid_obstacle < 2 and front_right_obstacle < 2) or \
                     (front_left_obstacle < 2 and front_mid_obstacle < 2):
                    print(self.log_string + text_color.WARNING + 'Recalibrating front' + text_color.ENDC)

                    # Get sensor data
                    send_param = "{\"dest\": \"arduino\", \"param\": \"F1\"}"

                    self.pc_cmd_conn.send(send_param.encode())
                    self.pc_cmd_conn.recv()
                    time.sleep(0.5)
                    self.pc_cmd_conn.recv()
                    print(self.log_string + text_color.OKGREEN + 'Recalibrate front done' + text_color.ENDC)

                # elif (front_mid_obstacle == 2 and front_right_obstacle < 2) or \
                #      (front_left_obstacle < 2 and front_mid_obstacle == 2):
                #     print(self.log_string + text_color.WARNING + 'Recalibrating step' + text_color.ENDC)

                #     # Get sensor data
                #     send_param = "{\"dest\": \"arduino\", \"param\": \"K1\"}"

                #     self.pc_cmd_conn.send(send_param.encode())
                #     self.pc_cmd_conn.recv()
                #     time.sleep(0.5)
                #     self.pc_cmd_conn.recv()
                #     print(self.log_string + text_color.OKGREEN + 'Recalibrate step done' + text_color.ENDC)
                #     return

                right_wall_counter = 0

            else:
                log_movement = 'forward'
                right_wall_counter += 1
                self.explorer.round = 1

                if (right_wall_counter % 4 == 0) and (right_front_obstacle < 2 and right_back_obstacle < 2):
                    print(self.log_string + text_color.WARNING + 'Recalibrating right wall' + text_color.ENDC)

                    # Calibrate right
                    send_param = "{\"dest\": \"arduino\",\"param\": \"R1\"}"

                    self.pc_cmd_conn.send(send_param.encode())
                    self.pc_cmd_conn.recv()
                    time.sleep(0.5)
                    self.pc_cmd_conn.recv()

                    right_wall_counter = 0
                    print(self.log_string + text_color.OKGREEN + 'Recalibrate right wall done' + text_color.ENDC)

            print(self.log_string + text_color.BOLD + 'Moving {}'.format(log_movement) + text_color.ENDC)

            # Convert explored map into hex
            hex_exp_map = self.explorer.convert_map_to_hex(self.explorer.explored_map)
            hex_real_map = self.explorer.convert_map_to_hex(self.explorer.real_map)

            packet = "{\"dest\": \"bt\",  \
                       \"explored\": \"" + hex_exp_map + "\",  \
                       \"obstacle\": \"" + hex_real_map + "\",  \
                       \"movement\": \"" + log_movement[0] + "\",  \
                       \"direction\": \"" + self.explorer.direction + "\"}"

            self.write_cmd_pc(packet.encode())
            self.pc_cmd_conn.recv()
            print(self.log_string + text_color.OKGREEN + 'Packet sent' + text_color.ENDC)

            # Get sensor data
            send_param = "{\"dest\": \"arduino\", \"param\": \"" + movement + "\"}"

            self.pc_cmd_conn.send(send_param.encode())
            self.pc_cmd_conn.recv()

        print(self.log_string + text_color.OKGREEN + 'Explore completed' + text_color.ENDC)

        # Convert real map to hex
        hex_real_map = self.explorer.convert_map_to_hex(self.explorer.real_map)
        hex_exp_map = self.explorer.convert_map_to_hex(self.explorer.explored_map)

        start = [[2, 2], [2, 1], [2, 0], [1, 2], [1, 1], [1, 0], [0, 2], [0, 1], [0, 0]]
        start_point = Point(int(start[4][0]), int(start[4][1]))
        end_point = Point(int(self.waypt_coord[0]), int(self.waypt_coord[1]))
        print("Computing fastest path!")
        for _ in range(2):
            a_star = AStar(start_point, end_point, self.explorer.real_map)
            start_pt = AStar.Node(start_point, end_point, 0)
            a_star.open_list.append(start_pt)

            while not flag:
                a_star.current = a_star.select_current()
                flag = a_star.near_explore(a_star.current)

            print(a_star.path)
            # print(start_point.x, start_point.y)
            # print(end_point.x, end_point.y)
            # print(self.explorer.real_map)

            for node_path in a_star.path:
                movements = self.move_to_point(node_path.point)
                for ele in movements:
                    path.append(ele)

            start_point = Point(self.explorer.current_pos[4][0], self.explorer.current_pos[4][1])
            end_point = Point(self.explorer.goal[4][0], self.explorer.goal[4][1])

        self.path_string = '{'
        count = 0
        for i in range(len(path)):
            if path[i] == 'W':
                count += 1
            elif path[i] != 'W' and path[i-1] == 'W':
                if count != 0:
                    self.path_string += '{}:{},'.format('W', str(count))
                self.path_string += '{}:{},'.format(path[i], '1')
                count = 0
            else:
                self.path_string += '{}:{},'.format(path[i], '1')
        
        self.path_string = self.path_string[:-1]
        self.path_string += '}'

        packet = "{\"dest\": \"rpi\",\"param\": \"S\"}"
        self.pc_cmd_conn.send(packet.encode())
        self.pc_cmd_conn.recv()

        image_id = self.pc_cmd_conn.recv().decode()

        packet = "{\"dest\": \"bt\", \"obstacle\": \"" + hex_real_map + "\", \"explored\": \"" + hex_exp_map + "\", \"Image_id\": \"" + image_id + "\"}"

        self.pc_cmd_conn.send(packet.encode())
        self.pc_cmd_conn.recv()

        # Save real map once done exploring
        self.explorer.save_map(hex_real_map)

        self.pc_cmd_conn.send('end'.encode())
        self.pc_cmd_conn.recv()

        if self.explorer.direction == Direction.E:
            send_param = "{\"dest\": \"arduino\",\"param\": \"N1\"}"
            self.pc_cmd_conn.send(send_param.encode())
            self.pc_cmd_conn.recv()
            time.sleep(0.5)
            self.pc_cmd_conn.recv()

        else:
            send_param = "{\"dest\": \"arduino\",\"param\": \"A1\"}"
            self.explorer.update_dir(True)
            elf.pc_cmd_conn.send(send_param.encode())
            self.pc_cmd_conn.recv()
            time.sleep(0.5)
            self.pc_cmd_conn.recv()
            send_param = "{\"dest\": \"arduino\",\"param\": \"N1\"}"
            self.pc_cmd_conn.send(send_param.encode())
            self.pc_cmd_conn.recv()
            time.sleep(0.5)
            self.pc_cmd_conn.recv()

        send_param = "{\"dest\": \"arduino\",\"param\": \"A2\"}"
        self.pc_cmd_conn.send(send_param.encode())
        self.pc_cmd_conn.recv()
        time.sleep(0.5)
        self.pc_cmd_conn.recv()
        time.sleep(0.5)
        self.pc_cmd_conn.recv()

    def move_to_point(self, point):

        movement = []

        # Comparing x axis
        if self.explorer.current_pos[4][0] != point.x:
            more = self.explorer.current_pos[4][0] - point.x

            # Turn left if more
            if more > 0:
                movement.append("A")
                movement.append("W")

            # Turn right if less
            else:
                movement.append("D")
                movement.append("W")

        # Comparing y axis
        elif self.explorer.current_pos[4][1] != point.y:
            more = self.explorer.current_pos[4][1] - point.y

            # Move forward if more
            if more > 0:
                movement.append("W")

            # Move backward if less
            else:
                movement.append("S")

        self.explorer.current_pos[4][0] = point.x
        self.explorer.current_pos[4][1] = point.y

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
    import sys
    try:
        main = Main(platform.system())
        # main = Main('Windows')
        if len(sys.argv) == 1:
            main.start()
        else:
            main.start(sys.argv[1])
        main.keep_main_alive()
    except KeyboardInterrupt:
        print("Program ending")
        #os.system('pkill -9 python')

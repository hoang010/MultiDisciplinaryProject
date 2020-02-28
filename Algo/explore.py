from ast import literal_eval
import numpy as np
import os
import queue
import json


class Explore:
    def __init__(self, direction_class):
        """
        Function to initialise an instance of Explore
        :param direction_class: Class
                Class containing directions
        """
        self.direction_class = direction_class
        self.direction = self.direction_class.N
        self.move_queue = queue.Queue()
        self.map_size = (15, 20)
        self.real_map = np.zeros(self.map_size)
        self.explored_map = self.real_map
        self.round = 0
        self.path = (0, 0)

        self.true_start = [(2, 2), (1, 2), (0, 2),
                           (2, 1), (1, 1), (0, 1),
                           (2, 0), (1, 0), (0, 0)]

        self.start = self.true_start

        # Follows format (y, x)
        # Since map is (15, 20), i.e. 15 rows x 20 columns then lim(y) = 15, lim(x) = 20,
        # then coordinates are as follows:
        # (17, 12)[front left], (17, 13)[front middle], (17, 14)[front right],
        # (18, 12)[middle left], (18, 13)[middle middle], (18, 14)[middle right],
        # (19, 12)[back left], (19, 13)[back middle], (19, 14)[back right]
        # This is done assuming the goal is at the bottom right of the map wrt numpy array
        self.goal = [(len(self.real_map[0]) - 3, len(self.real_map) - 3),
                     (len(self.real_map[0]) - 2, len(self.real_map) - 3),
                     (len(self.real_map[0]) - 1, len(self.real_map) - 3),

                     (len(self.real_map[0]) - 3, len(self.real_map) - 2),
                     (len(self.real_map[0]) - 2, len(self.real_map) - 2),
                     (len(self.real_map[0]) - 1, len(self.real_map) - 2),

                     (len(self.real_map[0]) - 3, len(self.real_map) - 1),
                     (len(self.real_map[0]) - 2, len(self.real_map) - 1),
                     (len(self.real_map[0]) - 1, len(self.real_map) - 1)]

        self.current_pos = self.start

    def right_wall_hugging(self, sensor_data):
        """
        Function to execute right wall hugging
        :param sensor_data: Array
                Array containing sensor data in cm
        :return:
        """

        # Get the data
        front_left_obstacle = int(sensor_data["TopLeft"])/10
        front_mid_obstacle = int(sensor_data["TopMiddle"])/10
        front_right_obstacle = int(sensor_data["TopRight"])/10
        mid_left_obstacle = int(sensor_data["LeftSide"])/10
        mid_right_obstacle = int(sensor_data["RightSide"])/10

        # Initialise variable for obstacle coordinates
        obstacle_coord = None

        # Initialise variable for explored coordinates
        explored_coord = self.current_pos

        # Get coordinates on the right
        right_x, right_y = self.get_coord('right')

        # Check if coordinates on right is within map
        if right_x < len(self.explored_map[0]) or right_y < len(self.explored_map):
            if right_x >= 0 and right_y >= 0:
                turn_right_condition = (mid_right_obstacle > 2 and self.explored_map[right_x][right_y] == 0)

        # If not within map, then just check if robot is near right wall
        else:
            turn_right_condition = mid_right_obstacle > 2

        # If there is no obstacle on the right
        if turn_right_condition is True:

            # Turn right (5 is the index to tell Arduino to turn right)
            movement = b'5'

            # Put the command 'right' into queue for main() to read
            self.move_queue.put(movement)

            # Update robot direction
            self.update_dir(left_turn=False)

        # If there is an obstacle in front and on the right
        elif front_left_obstacle < 2 or front_mid_obstacle < 2 or front_right_obstacle < 2:

            # Turn left (4 is the index to tell Arduino to turn left)
            movement = b'4'

            # Since there is an obstacle on the right, get the coordinates
            x_coord, y_coord = self.get_coord('right')

            # Check if right side coordinates are within boundaries
            if x_coord >= 0 or y_coord >= 0:
                if x_coord < len(self.real_map[0]) or y_coord < len(self.real_map):
                    # Add into array for obstacle coordinates
                    obstacle_coord.append((x_coord, y_coord))

            # Get obstacle coordinates and add into array for obstacle coordinates
            obstacle_coord.append(self.get_obstacle_coord(front_left_obstacle,
                                                          front_mid_obstacle,
                                                          front_right_obstacle))

            # Put the command 'left' into queue for main() to read
            self.move_queue.put(movement)

            # Update robot direction
            self.update_dir(left_turn=True)

        # If obstacle on right and no obstacle in front
        else:
            # Since there is an obstacle on the right, get the coordinates
            x_coord, y_coord = self.get_coord('right')

            # Check if right side coordinates are within boundaries
            if x_coord >= 0 or y_coord >= 0:
                if x_coord < len(self.real_map[0]) or y_coord < len(self.real_map):
                    # Add into array for obstacle coordinates
                    obstacle_coord.append((x_coord, y_coord))

            # Move forward (3 is the index to tell Arduino to move forward)
            movement = b'3'

            # Put the command 'advance' into queue for main() to read
            self.move_queue.put(movement)

            # Update position after moving
            self.update_pos()

        # Get left side coordinates
        left_coord = self.get_coord('left')

        # If it is an obstacle, append to array for obstacle
        if mid_left_obstacle == 1:
            obstacle_coord.append(left_coord)

        # Otherwise append to array for explore map
        explored_coord.append(left_coord)

        # Update map once done
        self.update_map(explored_coord, obstacle_coord)

        # if round is started and robot has moved from start position, set round to 1
        if not self.round and movement == '3':
            self.round = 1

    def update_pos(self):
        """
        Function to update current position according to the direction
        :return:
        """
        # If current direction is North
        if self.direction == self.direction_class.N:
            # Return (x, y+1)
            for i in range(len(self.current_pos)):
                self.current_pos[i][1] += 1

        # If current direction is South
        elif self.direction == self.direction_class.S:
            # Return (x, y-1)
            for i in range(len(self.current_pos)):
                self.current_pos[i][1] -= 1

        # If current direction is East
        elif self.direction == self.direction_class.E:
            # Return (x-1, y)
            for i in range(len(self.current_pos)):
                self.current_pos[i][0] -= 1

        # If current direction is West
        else:
            # Return (x+1, y)
            for i in range(len(self.current_pos)):
                self.current_pos[i][0] += 1

    def update_map(self, coord_array, obstacle):
        """
        Function to update explored map and real map
        :param coord_array: Array
                Array containing explored coordinates
        :param obstacle: Array
                Array containing obstacle coordinates
        :return:
        """
        # For every (x, y) pair in coord_array, set its location
        # in explored_map to 1
        for x, y in coord_array:
            self.explored_map[x][y] = 1

        # For every (x, y) pair in obstacle, set its location
        # in real_map to 1
        if obstacle:
            for x, y in obstacle:
                self.real_map[x][y] = 1

    def update_dir(self, left_turn):
        """
        Function to update direction of robot
        :param left_turn: String
                True if robot took a left turn,
                False otherwise
        :return:
        """

        def left():
            # If current direction is North, North turning to left is West
            if self.direction == self.direction_class.N:
                # Change current direction to West
                self.direction = self.direction_class.W

            # If current direction is South, North turning to left is East
            elif self.direction == self.direction_class.S:
                # Change current direction to East
                self.direction = self.direction_class.E

            # If current direction is East, North turning to left is South
            elif self.direction == self.direction_class.E:
                # Change current direction to South
                self.direction = self.direction_class.S

            # If current direction is West, North turning to left is North
            else:
                # Change current direction to North
                self.direction = self.direction_class.N

        def right():
            # If current direction is North, North turning to right is East
            if self.direction == self.direction_class.N:
                # Change current direction to East
                self.direction = self.direction_class.E

            # If current direction is South, North turning to right is West
            elif self.direction == self.direction_class.S:
                # Change current direction to West
                self.direction = self.direction_class.W

            # If current direction is East, North turning to right is North
            elif self.direction == self.direction_class.E:
                # Change current direction to North
                self.direction = self.direction_class.N

            # If current direction is West, North turning to right is South
            else:
                # Change current direction to South
                self.direction = self.direction_class.S

        if left_turn:
            left()
        else:
            right()

    def get_obstacle_coord(self, front_left, front_mid, front_right):
        """
        Function to get obstacle coordinate
        :param front_left: String
                number of obstacle is away from sensor
        :param front_mid: String
                number of obstacle is away from sensor
        :param front_right: String
                number of obstacle is away from sensor
        :return: obstacle: Array
                obstacle coordinates
        """

        obs_bool = [front_left, front_mid, front_right]
        obstacle = []

        for i in range(2, -1, -1):
            if obs_bool[i] != 0:
                # If current direction is North
                if self.direction == self.direction_class.N:
                    # Return (x, y+1)
                    obstacle.append((self.current_pos[i][0], self.current_pos[i][1] + int(obs_bool[i])))

                # If current direction is South
                elif self.direction == self.direction_class.S:
                    # Return (x, y-1)
                    obstacle.append((self.current_pos[i][0], self.current_pos[i][1] - int(obs_bool[i])))

                # If current direction is East
                elif self.direction == self.direction_class.E:
                    # Return (x-1, y)
                    obstacle.append((self.current_pos[i][0] - int(obs_bool[i]), self.current_pos[i][1]))

                # If current direction is West
                else:
                    # Return (x+1, y)
                    obstacle.append((self.current_pos[i][0] + int(obs_bool[i]), self.current_pos[i][1]))

        return obstacle

    def get_coord(self, direction):
        """
        Function to get coordinates on left/right/front of robot based on direction robot is facing
        :param direction: String
                String containing the side of robot coordinates should be retrieved from
        :return: coord: Array
                Array containing coordinates
        """

        def left():
            if self.direction == self.direction_class.N:
                # Return (x+1, y)
                coord = (self.current_pos[3][0] + 1, self.current_pos[3][1])

            # If current direction is South
            elif self.direction == self.direction_class.S:
                # Return (x-1, y)
                coord = (self.current_pos[3][0] - 1, self.current_pos[3][1])

            # If current direction is East
            elif self.direction == self.direction_class.E:
                # Return (x, y -1)
                coord = (self.current_pos[3][0], self.current_pos[3][1] + 1)

            # If current direction is West
            else:
                # Return (x, y + 1)
                coord = (self.current_pos[3][0], self.current_pos[3][1] - 1)

            return coord

        def right():
            if self.direction == self.direction_class.N:
                # Return (x-1, y)
                coord = (self.current_pos[5][0] - 1, self.current_pos[5][1])

            # If current direction is South
            elif self.direction == self.direction_class.S:
                # Return (x+1, y)
                coord = (self.current_pos[5][0] + 1, self.current_pos[5][1])

            # If current direction is East
            elif self.direction == self.direction_class.E:
                # Return (x, y+1)
                coord = (self.current_pos[5][0], self.current_pos[5][1] - 1)

            # If current direction is West
            else:
                # Return (x, y + 1)
                coord = (self.current_pos[5][0], self.current_pos[5][1] + 1)

            return coord

        def front():
            if self.direction == self.direction_class.N:
                # Return (x, y+1)
                coord = [(self.current_pos[0][0], self.current_pos[0][1] + 1),
                         (self.current_pos[1][0], self.current_pos[1][1] + 1),
                         (self.current_pos[2][0], self.current_pos[2][1] + 1)]

            # If current direction is South
            elif self.direction == self.direction_class.S:
                # Return (x, y-1)
                coord = [(self.current_pos[0][0], self.current_pos[0][1] - 1),
                         (self.current_pos[1][0], self.current_pos[1][1] - 1),
                         (self.current_pos[2][0], self.current_pos[2][1] - 1)]

            # If current direction is East
            elif self.direction == self.direction_class.E:
                # Return (x+1, y)
                coord = [(self.current_pos[0][0] + 1, self.current_pos[0][1]),
                         (self.current_pos[1][0] + 1, self.current_pos[1][1]),
                         (self.current_pos[2][0] + 1, self.current_pos[2][1])]

            # If current direction is West
            else:
                # Return (x-1, y)
                coord = [(self.current_pos[0][0] - 1, self.current_pos[0][1]),
                         (self.current_pos[1][0] - 1, self.current_pos[1][1]),
                         (self.current_pos[2][0] - 1, self.current_pos[2][1])]

            return coord

        if direction == 'left':
            return left()
        elif direction == 'right':
            return right()
        else:
            return front()

    def is_map_complete(self):
        """
        Function to check if map is complete
        :return: Boolean
                True if complete, False otherwise
        """
        # Sum up every element of the matrix
        # If every element is 1, it means that every element is explored and sum should be 300 (15 x 20).
        if self.explored_map.sum() == 300:
            self.save_map(self.explored_map)
            self.save_map(self.real_map)
            return True
        return False

    def check_round_complete(self):
        """
        Function to check if round is complete and reset self.round if round is complete
        :return:
        """

        # If round is complete, reset self.round to 0
        if self.current_pos[4] == self.start[4] and self.round == 1:
            self.round = 0
            return True
        return False

    def update_start(self, x, y):
        """
        Function to update start given a set of offsets
        :param x: int
                Integer containing how much to shift the start in the x direction
        :param y: int
                Integer containing how much to shift the start in the y direction
        :return:
        """

        # Increment all coordinates of the robot by x, y amounts
        for i in range(len(self.start)):
            self.start[i][0] += x
            self.start[i][1] += y

        # Finally, set the current position to be at the start
        self.current_pos = self.start

    def reset(self):
        """
        Function to reset all properties to initial state
        :return:
        """
        self.real_map = np.zeros(self.map_size)
        self.explored_map = np.zeros(self.map_size)
        self.path = (0, 0)
        self.start = self.current_pos

    def check_start(self):
        """
        Function to check if robot is at shifted start
        :return:
        """
        if self.current_pos[4] == self.start[4]:
            return True
        return False

    def move_to_point(self, log_string, text_color, arduino_conn, start):
        """
        Function to move robot to the specified point
        :param log_string: String
                String containing format of log
        :param text_color: Class
                Class containing String color format
        :param arduino_conn: Serial
                Connection to Arduino via USB
        :param start: Array
                Start point, can be all 9 points of position or just 1 reference start point
        :return:
        """

        print(log_string + text_color.WARNING + 'Move to point {}'.format(start[4]) + text_color.ENDC)

        # Execute loop while difference is not zero
        while not self.check_start():

            print(log_string + text_color.BOLD + 'Get sensor data' + text_color.ENDC)

            # Get info about surrounding
            send_param = b'2'
            arduino_conn.to_send_queue.put(send_param)
            sensor_data = arduino_conn.have_recv_queue.get()

            print(log_string + text_color.OKGREEN + 'Sensor data received' + text_color.ENDC)

            # Get the data
            sensor_data = literal_eval(sensor_data.decode())
            sensor_data = json.dumps(sensor_data, indent=4, sort_keys=True)

            front_left_obstacle = int(sensor_data["TopLeft"]) / 10
            front_mid_obstacle = int(sensor_data["TopMiddle"]) / 10
            front_right_obstacle = int(sensor_data["TopRight"]) / 10
            mid_left_obstacle = int(sensor_data["LeftSide"]) / 10
            mid_right_obstacle = int(sensor_data["RightSide"]) / 10

            start_has_obstacle = self.check_obstacle(sensor_data)

            # If there is, update start by 1 in x direction and skip the loop
            if start_has_obstacle:
                print(log_string + text_color.WARNING + 'Obstacle encountered' + text_color.ENDC)
                self.update_start(1, 0)
                print(log_string + text_color.BOLD + 'Updated start by 1 in x direction' + text_color.ENDC)
                continue

            # Check if front has obstacle
            front_obstacle = (front_left_obstacle < 1 or front_mid_obstacle < 1 or front_right_obstacle < 1)

            # If there is an obstacle in front
            if front_obstacle:

                # If there is no obstacle on the left
                if mid_left_obstacle > 10:

                    print(log_string + text_color.BOLD + 'Turning left' + text_color.ENDC)

                    # Tell Arduino to turn left
                    movement = b'4'

                    # Update direction
                    self.update_dir(True)

                # If there is obstacle on both left and right
                elif mid_right_obstacle:

                    # This shouldn't happen, but raise error if it does
                    raise Exception('GG: Dead End!')

                # If there is obstacle in front and no obstacle on right
                else:

                    print(log_string + text_color.BOLD + 'Turning right' + text_color.ENDC)
                    # Turn right
                    movement = b'5'

                    # Update direction
                    self.update_dir(False)

            # If no obstacle in front
            else:

                # Advance
                print(log_string + text_color.BOLD + 'Moving forward' + text_color.ENDC)
                movement = b'3'

                self.update_pos()

            # Tell arduino desired movement
            arduino_conn.to_send_queue.put(movement)

            # Get feedback
            _ = arduino_conn.have_recv_queue.get()

    def check_obstacle(self, sensor_data):

        front_left_obstacle = int(sensor_data["TopLeft"]) / 10
        front_mid_obstacle = int(sensor_data["TopMiddle"]) / 10
        front_right_obstacle = int(sensor_data["TopRight"]) / 10
        front_coord = self.get_coord('front')

        if self.direction == self.direction.N:
            return ((front_coord[0][1] + front_left_obstacle) in self.start or
                    (front_coord[1][1] + front_mid_obstacle) in self.start or
                    (front_coord[2][1] + front_right_obstacle) in self.start)
        elif self.direction == self.direction.S:
            return ((front_coord[0][1] - front_left_obstacle) in self.start or
                    (front_coord[1][1] - front_mid_obstacle) in self.start or
                    (front_coord[2][1] - front_right_obstacle) in self.start)
        elif self.direction == self.direction.E:
            return ((front_coord[0][0] + front_left_obstacle) in self.start or
                    (front_coord[1][0] + front_mid_obstacle) in self.start or
                    (front_coord[2][0] + front_right_obstacle) in self.start)
        else:
            return ((front_coord[0][0] - front_left_obstacle) in self.start or
                    (front_coord[1][0] - front_mid_obstacle) in self.start or
                    (front_coord[2][0] - front_right_obstacle) in self.start)

    @staticmethod
    def save_map(hex_map):
        """
        Function to save the map in hexadecimal form
        :param hex_map: String
                String containing the map in hex
        :return:
        """
        directory = './Maps'

        # If no Maps directory, create it
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Get number of files already in Maps sub-folder
        num = len([name for name in os.listdir(directory) if os.path.isfile(name)])

        # Open/Create a file with Map <num>.txt
        f = open(directory + 'Map {}.txt'.format(num), 'w+')

        # Save it to the opened file
        f.write('{}\n'.format(hex_map))

        # Close the file
        f.close()

    @staticmethod
    def convert_map_to_hex(bin_map):
        # As bin_map is a np array
        # Have to convert it to string before processing it
        # For each row in self.explored_map

        # Initialise variables
        hex_array = []
        hex_map = ''

        # Convert each array into string
        for i in range(len(bin_map)):
            temp = bin_map[i].astype(str).tolist()
            for j in range(len(bin_map[i])):
                temp = temp[j][-1]
            temp = ''.join(temp)
            hex_array.append(temp)

        # Then append all the combined strings in the array
        hex_array = '11' + ''.join(hex_array) + '11'

        # Converting the binary string into hex
        for i in range(0, len(hex_array), 8):
            j = 1 + 8
            hex_map += hex(int(hex_array[i:j], 2))[2:].zfill(2)

        # Return the hex coded string
        return hex_map

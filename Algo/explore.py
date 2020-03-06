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
        self.real_map = np.zeros((15, 20))
        self.explored_map = self.real_map.copy()
        self.round = 0

        self.true_start = [[2, 2], [1, 2], [0, 2],
                           [2, 1], [1, 1], [0, 1],
                           [2, 0], [1, 0], [0, 0]]

        self.start = self.true_start.copy()
        self.check_right_empty = 0

        self.goal = [[19, 14], [19, 13], [19, 12],
                     [18, 14], [18, 13], [18, 12],
                     [17, 14], [17, 13], [17, 14]]

        self.current_pos = self.start.copy()

    def right_wall_hugging(self, sensor_data):
        """
        Function to execute right wall hugging
        :param sensor_data: Array
                Array containing sensor data in cm
        :return:
        """

        # Get the data
        front_left_obstacle = round(sensor_data["FrontLeft"]/10)
        front_mid_obstacle = round(sensor_data["FrontCenter"]/10)
        front_right_obstacle = round(sensor_data["FrontRight"]/10)
        mid_left_obstacle = round(sensor_data["LeftSide"]/10)
        right_front_obstacle = round(sensor_data["RightFront"]/10)
        right_back_obstacle = round(sensor_data["RightBack"]/10)

        # Initialise variable for obstacle coordinates
        obstacle_coord = []

        # Initialise variable for explored coordinates
        explored_coord = self.current_pos.copy()

        # Get coordinates on the right
        coordinates = self.get_coord('right')

        # Check if coordinates on right is within map
        frontx_in_map = bool(len(self.explored_map) > coordinates[0][0] > -1)
        fronty_in_map = bool(len(self.explored_map[0]) > coordinates[0][1] > -1)
        backx_in_map = bool(len(self.explored_map) > coordinates[1][0] > -1)
        backy_in_map = bool(len(self.explored_map[0]) > coordinates[1][1] > -1)
        front_in_map = bool(frontx_in_map and fronty_in_map)
        back_in_map = bool(backx_in_map and backy_in_map)

        # Check if there is obstacle on right
        obs_on_right = bool(right_back_obstacle < 2 or right_front_obstacle < 2)

        if front_in_map and back_in_map:
            unexplored_coord = bool(self.explored_map[coordinates[0][0]][coordinates[0][1]] == 0 or
                                    self.explored_map[coordinates[1][0]][coordinates[1][1]] == 0)

            turn_right = bool(not obs_on_right and
                              unexplored_coord and
                              self.check_right_empty > 2)

        # If not within map, then just check if robot is near right wall
        else:
            turn_right = bool(not obs_on_right and self.check_right_empty > 2)

        # If there is no obstacle on the right
        if turn_right:

            # Reset counter
            self.check_right_empty = 0

            # Turn right (5 is the index to tell Arduino to turn right)
            movement = '5'

            # Put the command 'right' into queue for main() to read
            self.move_queue.put(movement)

            # Update robot direction
            self.update_dir(left_turn=False)

        # If there is an obstacle in front and on the right
        elif front_left_obstacle < 1 or front_mid_obstacle < 1 or front_right_obstacle < 1:

            # Turn left (4 is the index to tell Arduino to turn left)
            movement = '4'

            if front_in_map:
                obstacle_coord.append(coordinates[0])

            if back_in_map:
                obstacle_coord.append(coordinates[1])

            # Get obstacle coordinates and add into array for obstacle coordinates
            front_coordinates = self.get_coord('front')

            if front_left_obstacle < 1:
                obstacle_coord.append(front_coordinates[0])

            if front_mid_obstacle < 1:
                obstacle_coord.append(front_coordinates[1])

            if front_right_obstacle < 1:
                obstacle_coord.append(front_coordinates[2])

            # Put the command 'left' into queue for main() to read
            self.move_queue.put(movement)

            # Update robot direction
            self.update_dir(left_turn=True)

        # If obstacle on right and no obstacle in front
        else:

            self.check_right_empty += 1

            if front_in_map:
                obstacle_coord.append(coordinates[0])

            if back_in_map:
                obstacle_coord.append(coordinates[1])

            # Move forward (3 is the index to tell Arduino to move forward)
            movement = '3'

            # Put the command 'advance' into queue for main() to read
            self.move_queue.put(movement)

            # Update position after moving
            self.update_pos()

        # Get left side coordinates
        left_coord = self.get_coord('left', mid_left_obstacle)

        # If it is an obstacle, append to array for obstacle
        if mid_left_obstacle < 6:
            coord = self.get_coord('left', mid_left_obstacle+1)
            obstacle_coord.append(coord[-1])

        if len(left_coord) > 1:
            # Otherwise append to array for explore map
            for array in left_coord:
                explored_coord.append(array)
        else:
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
            # Return (x+1, 1)
            for i in range(len(self.current_pos)):
                self.current_pos[i][0] += 1

        # If current direction is South
        elif self.direction == self.direction_class.S:
            # Return (x-1, y)
            for i in range(len(self.current_pos)):
                self.current_pos[i][0] -= 1

        # If current direction is East
        elif self.direction == self.direction_class.E:
            # Return (x, y-1)
            for i in range(len(self.current_pos)):
                self.current_pos[i][1] -= 1

        # If current direction is West
        else:
            # Return (x, y+1)
            for i in range(len(self.current_pos)):
                self.current_pos[i][1] += 1

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
        for coordinates in coord_array:
            self.explored_map[coordinates[1]][coordinates[0]] = 1

        # For every (x, y) pair in obstacle, set its location
        # in real_map to 1
        if obstacle:
            for coordinates in obstacle:
                self.real_map[coordinates[1]][coordinates[0]] = 1

    def update_dir(self, left_turn):
        """
        Function to update direction of robot
        :param left_turn: String
                True if robot took a left turn,
                False otherwise
        :return:
        """

        if left_turn:
            # If current direction is North, North turning to left is West
            if self.direction == self.direction_class.N:
                # Change current direction to West
                self.direction = self.direction_class.W

            # If current direction is South, South turning to left is East
            elif self.direction == self.direction_class.S:
                # Change current direction to East
                self.direction = self.direction_class.E

            # If current direction is East, East turning to left is North
            elif self.direction == self.direction_class.E:
                # Change current direction to North
                self.direction = self.direction_class.N

            # If current direction is West, West turning to left is South
            else:
                # Change current direction to South
                self.direction = self.direction_class.S

        else:
            # If current direction is North, North turning to right is East
            if self.direction == self.direction_class.N:
                # Change current direction to East
                self.direction = self.direction_class.E

            # If current direction is South, South turning to right is West
            elif self.direction == self.direction_class.S:
                # Change current direction to West
                self.direction = self.direction_class.W

            # If current direction is East, East turning to right is South
            elif self.direction == self.direction_class.E:
                # Change current direction to North
                self.direction = self.direction_class.S

            # If current direction is West, West turning to right is North
            else:
                # Change current direction to South
                self.direction = self.direction_class.N

    def get_coord(self, direction, dist=0):
        """
        Function to get coordinates on left/right/front of robot based on direction robot is facing
        :param direction: String
                String containing the side of robot coordinates should be retrieved from
        :param dist: int
                Integer containing distance of nearest obstacle away from robot
        :return: coord: Array
                Array containing coordinates
        """

        if direction == 'left':
            if self.direction == self.direction_class.N:
                # Return (x+1, y)
                if dist:
                    coord = []
                    for i in range(1, dist+1):
                        coord.append([self.current_pos[3][0] + i, self.current_pos[3][1]])
                    return coord
                else:
                    return [self.current_pos[3][0] + 1, self.current_pos[3][1]]

            # If current direction is South
            elif self.direction == self.direction_class.S:
                # Return (x-1, y)
                if dist:
                    coord = []
                    for i in range(1, dist+1):
                        coord.append([self.current_pos[3][0] - i, self.current_pos[3][1]])
                    return coord
                else:
                    return [self.current_pos[3][0] - 1, self.current_pos[3][1]]

            # If current direction is East
            elif self.direction == self.direction_class.E:
                # Return (x, y+1)
                if dist:
                    coord = []
                    for i in range(1, dist+1):
                        coord.append([self.current_pos[3][0], self.current_pos[3][1] + i])
                    return coord
                else:
                    return [self.current_pos[3][0], self.current_pos[3][1] + 1]

            # If current direction is West
            else:
                # Return (x, y + 1)
                if dist:
                    coord = []
                    for i in range(1, dist+1):
                        coord.append([self.current_pos[3][0], self.current_pos[3][1] - i])
                    return coord
                else:
                    return [self.current_pos[3][0], self.current_pos[3][1] - 1]

        elif direction == 'right':
            if self.direction == self.direction_class.N:
                # Return (x-1, y)
                return [[self.current_pos[2][0], self.current_pos[2][1] - 1],
                        [self.current_pos[8][0], self.current_pos[8][1] - 1]]

            # If current direction is South
            elif self.direction == self.direction_class.S:
                # Return (x+1, y)
                return [[self.current_pos[2][0], self.current_pos[2][1] + 1],
                        [self.current_pos[8][0], self.current_pos[8][1] + 1]]

            # If current direction is East
            elif self.direction == self.direction_class.E:
                # Return (x, y+1)
                return [[self.current_pos[2][0] + 1, self.current_pos[2][1]],
                        [self.current_pos[8][0] + 1, self.current_pos[8][1]]]

            # If current direction is West
            else:
                # Return (x, y + 1)
                return [[self.current_pos[2][0] - 1, self.current_pos[2][1]],
                        [self.current_pos[8][0] - 1, self.current_pos[8][1]]]

        elif direction == 'front':
            if self.direction == self.direction_class.N:
                # Return (x, y+1)
                return [[self.current_pos[0][0] + 1, self.current_pos[0][1]],
                        [self.current_pos[1][0] + 1, self.current_pos[1][1]],
                        [self.current_pos[2][0] + 1, self.current_pos[2][1]]]

            # If current direction is South
            elif self.direction == self.direction_class.S:
                # Return (x, y-1)
                return [[self.current_pos[0][0] - 1, self.current_pos[0][1]],
                        [self.current_pos[1][0] - 1, self.current_pos[1][1]],
                        [self.current_pos[2][0] - 1, self.current_pos[2][1]]]

            # If current direction is East
            elif self.direction == self.direction_class.E:
                # Return (x+1, y)
                return [[self.current_pos[0][0], self.current_pos[0][1] + 1],
                        [self.current_pos[1][0], self.current_pos[1][1] + 1],
                        [self.current_pos[2][0], self.current_pos[2][1] + 1]]

            # If current direction is West
            else:
                # Return (x-1, y)
                return [[self.current_pos[0][0], self.current_pos[0][1] - 1],
                        [self.current_pos[1][0], self.current_pos[1][1] - 1],
                        [self.current_pos[2][0], self.current_pos[2][1] - 1]]

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

    def reset(self):
        """
        Function to reset all properties to initial state
        :return:
        """
        self.real_map = np.zeros((15, 20))
        self.explored_map = np.zeros((15, 20))
        self.start = self.current_pos.copy()

    def check_start(self):
        """
        Function to check if robot is at shifted start
        :return:
        """
        if self.current_pos[4] == self.start[4]:
            return True
        return False

    def navigate_to_point(self, log_string, text_color, sensor_data, point):
        """
        Function to move robot to the specified point
        :param log_string: String
                String containing format of log
        :param text_color: Class
                Class containing String color format
        :param arduino_conn: Serial
                Connection to Arduino via USB
        :param sensor_data: Dict
                Dictionary containing sensor data
        :param point: Array
                Point to go to, can be all 9 points of position or just 1 reference start point
        :return:
        """

        print(log_string + text_color.WARNING + 'Move to point {}'.format(point[4]) + text_color.ENDC)

        print(log_string + text_color.BOLD + 'Get sensor data' + text_color.ENDC)

        print(log_string + text_color.OKGREEN + 'Sensor data received' + text_color.ENDC)

        # Get the data
        front_left_obstacle = round(sensor_data["FrontLeft"]/10)
        front_mid_obstacle = round(sensor_data["FrontCenter"]/10)
        front_right_obstacle = round(sensor_data["FrontRight"]/10)
        mid_left_obstacle = round(sensor_data["LeftSide"]/10)
        right_front_obstacle = round(sensor_data["RightFront"]/10)
        right_back_obstacle = round(sensor_data["RightBack"]/10)

        start_has_obstacle = self.check_obstacle(sensor_data)

        # If there is, update start by 1 in x direction and skip the loop
        if start_has_obstacle:
            print(log_string + text_color.WARNING + 'Obstacle encountered' + text_color.ENDC)
            self.update_start(1, 0)
            print(log_string + text_color.BOLD + 'Updated start by 1 in x direction' + text_color.ENDC)

        # Check if front has obstacle
        front_obstacle = bool(front_left_obstacle < 1 or front_mid_obstacle < 1 or front_right_obstacle < 1)

        # If there is an obstacle in front
        if front_obstacle:

            # If there is no obstacle on the left
            if mid_left_obstacle > 3:

                print(log_string + text_color.BOLD + 'Turning left' + text_color.ENDC)

                # Tell Arduino to turn left
                movement = "4"

                # Update direction
                self.update_dir(True)

            # If there is obstacle in front and no obstacle on right
            else:

                print(log_string + text_color.BOLD + 'Turning right' + text_color.ENDC)
                # Turn right
                movement = "5"

                # Update direction
                self.update_dir(False)

        # If no obstacle in front
        else:

            # Advance
            print(log_string + text_color.BOLD + 'Moving forward' + text_color.ENDC)
            movement = "3"

            self.update_pos()

        # Tell arduino desired movement
        self.move_queue.put(movement)

    def set_direction(self, direction):
        if self.direction != direction:
            # Turn left while direction is wrong
            self.move_queue.put("4")
            return False
        return True

    def check_obstacle(self, sensor_data):

        front_left_obstacle = round(sensor_data["TopLeft"]/10)
        front_mid_obstacle = round(sensor_data["TopMiddle"]/10)
        front_right_obstacle = round(sensor_data["TopRight"]/10)
        front_coord = self.get_coord('front')

        if self.direction == self.direction.N:
            return bool((front_coord[0][0] + front_left_obstacle) in self.start or
                        (front_coord[1][0] + front_mid_obstacle) in self.start or
                        (front_coord[2][0] + front_right_obstacle) in self.start)
        elif self.direction == self.direction.S:
            return bool((front_coord[0][0] - front_left_obstacle) in self.start or
                        (front_coord[1][0] - front_mid_obstacle) in self.start or
                        (front_coord[2][0] - front_right_obstacle) in self.start)
        elif self.direction == self.direction.E:
            return bool((front_coord[0][1] + front_left_obstacle) in self.start or
                        (front_coord[1][1] + front_mid_obstacle) in self.start or
                        (front_coord[2][1] + front_right_obstacle) in self.start)
        else:
            return bool((front_coord[0][1] - front_left_obstacle) in self.start or
                        (front_coord[1][1] - front_mid_obstacle) in self.start or
                        (front_coord[2][1] - front_right_obstacle) in self.start)

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
                temp[j] = temp[j][-1]
            temp = ''.join(temp)
            hex_array.append(temp)

        # Then append all the combined strings in the array
        hex_array = '11' + ''.join(hex_array) + '11'

        # Converting the binary string into hex
        for i in range(0, len(hex_array), 4):
            j = i + 4
            hex_map += hex(int(hex_array[i:j], 2))[2:]

        # Return the hex coded string
        return hex_map

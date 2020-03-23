import numpy as np
import os
import queue
import threading


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

        self.true_start = [[2, 2], [2, 1], [2, 0],
                           [1, 2], [1, 1], [1, 0],
                           [0, 2], [0, 1], [0, 0]]

        self.round = 0
        self.check_right_empty = 0
        self.current_pos = self.true_start.copy()

        self.goal = [[19, 14], [19, 13], [19, 12],
                     [18, 14], [18, 13], [18, 12],
                     [17, 14], [17, 13], [17, 14]]

        self.sensor_data_queue = queue.Queue()
        #self.explored_coord_queue = queue.Queue()
        #self.obstacle_coord_queue = queue.Queue()

        self.explore_thread = threading.Thread(target=self.right_wall_hugging_no_thread)
        #self.update_explored_map_thread = threading.Thread(target=self.update_explored_map)
        #self.update_obstacle_map_thread = threading.Thread(target=self.update_obstacle_map)

        self.explore_thread.start()
        #self.update_explored_map_thread.start()
        #self.update_obstacle_map_thread.start()

    def right_wall_hugging_no_thread(self):
        """
        Function to execute right wall hugging
        :return:
        """

        start = [[2, 2], [2, 1], [2, 0],
                 [1, 2], [1, 1], [1, 0],
                 [0, 2], [0, 1], [0, 0]]

        while not self.is_round_complete(start):

            sensor_data = self.sensor_data_queue.get()

            # Get the data
            front_left_obstacle = round(sensor_data["FrontLeft"]/10)
            front_mid_obstacle = round(sensor_data["FrontCenter"]/10)
            front_right_obstacle = round(sensor_data["FrontRight"]/10)
            mid_left_obstacle = round((sensor_data["LeftSide"])/10)
            right_front_obstacle = round(sensor_data["RightFront"]/10)
            right_back_obstacle = round(sensor_data["RightBack"]/10)

            # Get coordinates on the right
            right_coordinates = self.get_coord('right')

            if right_front_obstacle < 2:
                self.update_obstacle_map_no_thread(right_coordinates[0])

            if right_back_obstacle < 2:
                self.update_obstacle_map_no_thread(right_coordinates[1])

            # If reading is 151, append up to max range of 9
            if mid_left_obstacle > 8:
                print("Updating long left")
                # Get left side coordinates
                left_coord = self.get_coord('left', 7)
                for i in range(len(left_coord)):
                    self.update_explored_map_no_thread(left_coord[i])

            # If it is an obstacle, append to array for obstacle
            elif 2 <= mid_left_obstacle <= 8:
                print("Updating long left too far")
                #the plus 1 is for the last coor to be obstacle
                coord = self.get_coord('left', mid_left_obstacle +1)
                self.update_obstacle_map_no_thread(coord[-1])
                for i in range(len(coord)):
                    self.update_explored_map_no_thread(coord[i])

            if front_left_obstacle <= 4:
                print("Updating front left")
                front_left_coord = self.get_coord('front', front_left_obstacle + 1, 3)
                for i in range(0, len(front_left_coord)):
                    self.update_explored_map_no_thread(front_left_coord[i])
                    self.update_no_obstacle_map_no_thread(front_left_coord[i])
                self.update_obstacle_map_no_thread(front_left_coord[-1])

            else:
                print("Updating front left too far")
                front_left_coord = self.get_coord('front', 4, 3)
                for i in range(1, len(front_left_coord)):
                    self.update_explored_map_no_thread(front_left_coord[i])
                    self.update_no_obstacle_map_no_thread(front_left_coord[i])

            if front_mid_obstacle <= 4:
                print("Updating front mid")
                front_mid_coord = self.get_coord('front', front_mid_obstacle+1, 4)
                for i in range(2, len(front_mid_coord)):
                    self.update_explored_map_no_thread(front_mid_coord[i])
                    self.update_no_obstacle_map_no_thread(front_mid_coord[i])
                self.update_obstacle_map_no_thread(front_mid_coord[-1])

            else:
                print("Updating front mid too far")
                front_mid_coord = self.get_coord('front', 4, 4)
                for i in range(len(front_mid_coord)):
                    self.update_explored_map_no_thread(front_mid_coord[i])
                    self.update_no_obstacle_map_no_thread(front_mid_coord[i])

            if front_right_obstacle <= 4:
                print("Updating front right")
                front_right_coord = self.get_coord('front', front_right_obstacle+1, 5)
                for i in range(len(front_right_coord)):
                    self.update_explored_map_no_thread(front_right_coord[i])
                    self.update_no_obstacle_map_no_thread(front_right_coord[i])
                self.update_obstacle_map_no_thread(front_right_coord[-1])

            else:
                print("Updating front right too far")
                front_right_coord = self.get_coord('front', 4, 5)
                for i in range(len(front_right_coord)):
                    self.update_explored_map_no_thread(front_right_coord[i])
                    self.update_no_obstacle_map_no_thread(front_right_coord[i])

            self.update_explored_map_no_thread(right_coordinates[0])
            self.update_explored_map_no_thread(right_coordinates[1])

            # Check if there is obstacle on right
            obs_on_right = bool(right_back_obstacle < 2 or right_front_obstacle < 2)
            turn_right = bool(not obs_on_right and self.check_right_empty > 2)

            # If there is no obstacle on the right
            if turn_right:

                # Put the command 'right' into queue for main() to read
                self.move_queue.put('D1')

                # Reset counter
                self.check_right_empty = 0

                # Update robot direction
                self.update_dir(left_turn=False)

            # If there is an obstacle in front and on the right
            elif front_left_obstacle < 2 or front_right_obstacle < 2 or front_mid_obstacle <2:

                # Put the command 'left' into queue for main() to read
                self.move_queue.put('A1')

                # Update robot direction
                self.update_dir(left_turn=True)

            # If obstacle on right and no obstacle in front
            else:
                #If both right and back obstacle available then also calibrate after forward move
                if right_back_obstacle < 2 and right_front_obstacle < 2:
                    self.move_queue.put('Q1')
                else:
                    # case when cannot calibrate, move forward blindly
                    self.move_queue.put('W1')

                self.check_right_empty += 1

                # Update position after moving
                self.update_pos()


    def right_wall_hugging(self):
        """
        Function to execute right wall hugging
        :return:
        """

        start = [[2, 2], [2, 1], [2, 0],
                 [1, 2], [1, 1], [1, 0],
                 [0, 2], [0, 1], [0, 0]]

        while not self.is_round_complete(start):

            sensor_data = self.sensor_data_queue.get()

            # Get the data
            front_left_obstacle = round(sensor_data["FrontLeft"]/10)
            front_mid_obstacle = round(sensor_data["FrontCenter"]/10)
            front_right_obstacle = round(sensor_data["FrontRight"]/10)
            mid_left_obstacle = round((sensor_data["LeftSide"])/10)
            right_front_obstacle = round(sensor_data["RightFront"]/10)
            right_back_obstacle = round(sensor_data["RightBack"]/10)

            # Get coordinates on the right
            right_coordinates = self.get_coord('right')

            if right_front_obstacle < 2:
                self.obstacle_coord_queue.put(right_coordinates[0])

            if right_back_obstacle < 2:
                self.obstacle_coord_queue.put(right_coordinates[1])

            # If reading is 151, append up to max range of 9
            if mid_left_obstacle > 8:
                # Get left side coordinates
                left_coord = self.get_coord('left', 7)
                for i in range(len(left_coord)):
                    self.explored_coord_queue.put(left_coord[i])

            # If it is an obstacle, append to array for obstacle
            elif 2 <= mid_left_obstacle <= 8:
                #the plus 1 is for the last coor to be obstacle
                coord = self.get_coord('left', mid_left_obstacle +1)
                self.obstacle_coord_queue.put(coord[-1])
                for i in range(len(coord)):
                    self.explored_coord_queue.put(coord[i])

            if front_left_obstacle <= 4:
                front_left_coord = self.get_coord('front', front_left_obstacle+1, 3)
                self.obstacle_coord_queue.put(front_left_coord[-1])
                for i in range(0, len(front_left_coord), 3):
                    self.explored_coord_queue.put(front_left_coord[i])

            else:
                front_left_coord = self.get_coord('front', 4, 3)
                for i in range(1, len(front_left_coord)):
                    self.explored_coord_queue.put(front_left_coord[i])

            if front_mid_obstacle <= 4:
                front_mid_coord = self.get_coord('front', front_left_obstacle+1, 4)
                self.obstacle_coord_queue.put(front_mid_coord[-1])
                for i in range(2, len(front_mid_coord)):
                    self.explored_coord_queue.put(front_mid_coord[i])

            else:
                front_mid_coord = self.get_coord('front', 4, 4)
                for i in range(len(front_mid_coord)):
                    self.explored_coord_queue.put(front_mid_coord[i])

            if front_right_obstacle <= 4:
                front_right_coord = self.get_coord('front', front_left_obstacle+1, 5)
                self.obstacle_coord_queue.put(front_right_coord[-1])
                for i in range(len(front_right_coord)):
                    self.explored_coord_queue.put(front_right_coord[i])

            else:
                front_right_coord = self.get_coord('front', 4, 5)
                for i in range(len(front_right_coord)):
                    self.explored_coord_queue.put(front_right_coord[i])

            self.explored_coord_queue.put(right_coordinates[0])
            self.explored_coord_queue.put(right_coordinates[1])

            # Check if there is obstacle on right
            obs_on_right = bool(right_back_obstacle < 2 or right_front_obstacle < 2)
            turn_right = bool(not obs_on_right and self.check_right_empty > 2)

            # If there is no obstacle on the right
            if turn_right:

                # Put the command 'right' into queue for main() to read
                self.move_queue.put('D1')

                # Reset counter
                self.check_right_empty = 0

                # Update robot direction
                self.update_dir(left_turn=False)

            # If there is an obstacle in front and on the right
            elif front_left_obstacle < 2 or front_right_obstacle < 2 or front_mid_obstacle <2:

                # Put the command 'left' into queue for main() to read
                self.move_queue.put('A1')

                # Update robot direction
                self.update_dir(left_turn=True)

            # If obstacle on right and no obstacle in front
            else:
                #If both right and back obstacle available then also calibrate after forward move
                if right_back_obstacle < 2 and right_front_obstacle < 2:
                    self.move_queue.put('Q1')
                else:
                    # case when cannot calibrate, move forward blindly
                    self.move_queue.put('W1')

                self.check_right_empty += 1

                # Update position after moving
                self.update_pos()

    def check_in_map(self, x, y):
        return bool((len(self.explored_map) > x > -1) and
                    (len(self.explored_map[0]) > y > -1))

    def update_explored_map(self):
        """
        Function to update explored map and real map
        :return:
        """
        # Initialise variable for explored coordinates

        while True:
            for array in self.current_pos:
                if self.check_in_map(array[0], array[1]):
                    self.explored_map[array[0]][array[1]] = 1
            # For every (x, y) pair in coord_array, set its location
            # in explored_map to 1
            if not self.explored_coord_queue.empty():
                coordinates = self.explored_coord_queue.get()
                print("Explored coordinates: ", coordinates)
                if self.check_in_map(coordinates[0], coordinates[1]):
                    self.explored_map[coordinates[0]][coordinates[1]] = 1
    
    def update_explored_map_no_thread(self, coord):
        """
        Function to update explored map and real map
        :return:
        """
        # Initialise variable for explored coordinates

        for array in self.current_pos:
            if self.check_in_map(array[0], array[1]):
                self.explored_map[array[0]][array[1]] = 1
                self.real_map[array[0]][array[1]] = 0
        # For every (x, y) pair in coord_array, set its location
        # in explored_map to 1
        coordinates = coord
        print("Explored coordinates: ", coordinates)
        if self.check_in_map(coordinates[0], coordinates[1]):
            self.explored_map[coordinates[0]][coordinates[1]] = 1

    def update_obstacle_map_no_thread(self, coord):
        # For every (x, y) pair in obstacle, set its location
        # in real_map to 1

        coordinates = coord
        print("Obstacle coordinates", coordinates)
        if self.check_in_map(coordinates[0], coordinates[1]):
            self.real_map[coordinates[0]][coordinates[1]] = 1

    def update_no_obstacle_map_no_thread(self, coord):
        # For every (x, y) pair in obstacle, set its location
        # in real_map to 1

        coordinates = coord
        print("Obstacle coordinates", coordinates)
        if self.check_in_map(coordinates[0], coordinates[1]):
            self.real_map[coordinates[0]][coordinates[1]] = 0

    def update_obstacle_map(self):
        print("Not Used!!!!!")
        # For every (x, y) pair in obstacle, set its location
        # in real_map to 1
        while True:
            if not self.obstacle_coord_queue.empty():
                coordinates = self.obstacle_coord_queue.get()
                print("Obstacle coordinates", coordinates)
                if self.check_in_map(coordinates[0], coordinates[1]):
                    self.real_map[coordinates[0]][coordinates[1]] = 1

    def update_pos(self):
        """
        Function to update current position according to the direction
        :return:
        """
        # If current direction is North
        if self.direction == self.direction_class.N:
            # Return (x+1, 1)
            for i in range(9):
                self.current_pos[i][0] += 1

        # If current direction is South
        elif self.direction == self.direction_class.S:
            # Return (x-1, y)
            for i in range(9):
                self.current_pos[i][0] -= 1

        # If current direction is East
        elif self.direction == self.direction_class.E:
            # Return (x, y-1)
            for i in range(9):
                self.current_pos[i][1] -= 1

        # If current direction is West
        else:
            # Return (x, y+1)
            for i in range(9):
                self.current_pos[i][1] += 1

    def update_dir(self, left_turn):
        """
        Function to update direction of robot
        :param left_turn: String
                True if robot took a left turn,
                False otherwise
        :return:
        """
        temp = [[], [], [], [], [], [], [], [], []]
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

            temp[0] = self.current_pos[6]
            temp[1] = self.current_pos[3]
            temp[2] = self.current_pos[0]
            temp[3] = self.current_pos[7]
            temp[4] = self.current_pos[4]
            temp[5] = self.current_pos[1]
            temp[6] = self.current_pos[8]
            temp[7] = self.current_pos[5]
            temp[8] = self.current_pos[2]

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

            temp[0] = self.current_pos[2]
            temp[1] = self.current_pos[5]
            temp[2] = self.current_pos[8]
            temp[3] = self.current_pos[1]
            temp[4] = self.current_pos[4]
            temp[5] = self.current_pos[7]
            temp[6] = self.current_pos[0]
            temp[7] = self.current_pos[3]
            temp[8] = self.current_pos[6]

        self.current_pos = temp.copy()

    def get_coord(self, direction, dist=0, whichFront = 0):
        """
        Function to get coordinates on left/right/front of robot based on direction robot is facing
        :param direction: String
                String containing the side of robot coordinates should be retrieved from
        :param dist: int
                Integer containing distance of nearest obstacle away from robot
        :return: coord: Array
                Array containing coordinates
        """
        coord = []
        if direction == 'left':
            if self.direction == self.direction_class.N:
                if dist > 0:
                    for i in range(1, dist + 1):
                        coord.append([self.current_pos[2][0], self.current_pos[2][1] + i])

            # If current direction is South
            elif self.direction == self.direction_class.S:
                if dist > 0:
                    for i in range(1, dist+1):
                        coord.append([self.current_pos[2][0], self.current_pos[2][1]-i])

            # If current direction is East
            elif self.direction == self.direction_class.E:
                if dist > 0:
                    for i in range(1, dist+1):
                        coord.append([self.current_pos[2][0]+i, self.current_pos[2][1]])

            # If current direction is West
            else:
                if dist > 0:
                    for i in range(1, dist+1):
                        coord.append([self.current_pos[2][0]-i, self.current_pos[2][1]])


        elif direction == 'right':
            if self.direction == self.direction_class.N:
                # Return (x-1, y)
                coord = [[self.current_pos[2][0], self.current_pos[2][1] - 1],
                         [self.current_pos[8][0], self.current_pos[8][1] - 1]]

            # If current direction is South
            elif self.direction == self.direction_class.S:
                # Return (x+1, y)
                coord = [[self.current_pos[2][0], self.current_pos[2][1] + 1],
                         [self.current_pos[8][0], self.current_pos[8][1] + 1]]

            # If current direction is East
            elif self.direction == self.direction_class.E:
                # Return (x, y+1)
                coord = [[self.current_pos[2][0] - 1, self.current_pos[2][1]],
                         [self.current_pos[8][0] - 1, self.current_pos[8][1]]]

            # If current direction is West
            else:
                # Return (x, y + 1)
                coord = [[self.current_pos[2][0] + 1, self.current_pos[2][1]],
                         [self.current_pos[8][0] + 1, self.current_pos[8][1]]]

        elif direction == 'front':
            if self.direction == self.direction_class.N:
                # Return (x, y+1)
                if dist > 0:
                    for i in range(1, dist+1):
                        coord.append([self.current_pos[whichFront][0]+i, self.current_pos[whichFront][1]])
                else:
                    coord.append([self.current_pos[0][0] + 1, self.current_pos[0][1]])
                    coord.append([self.current_pos[1][0] + 1, self.current_pos[1][1]])
                    coord.append([self.current_pos[2][0] + 1, self.current_pos[2][1]])

            # If current direction is South
            elif self.direction == self.direction_class.S:
                # Return (x, y-1)
                if dist > 0:
                    for i in range(1, dist+1):
                        coord.append([self.current_pos[whichFront][0]-i, self.current_pos[whichFront][1]])
                else:
                    coord.append([self.current_pos[0][0] - 1, self.current_pos[0][1]])
                    coord.append([self.current_pos[1][0] - 1, self.current_pos[1][1]])
                    coord.append([self.current_pos[2][0] - 1, self.current_pos[2][1]])

            # If current direction is East
            elif self.direction == self.direction_class.E:
                # Return (x+1, y)
                if dist > 0:
                    for i in range(1, dist+1):
                        coord.append([self.current_pos[whichFront][0], self.current_pos[whichFront][1] - i])
                else:
                    coord.append([self.current_pos[0][0], self.current_pos[0][1] - 1])
                    coord.append([self.current_pos[1][0], self.current_pos[1][1] - 1])
                    coord.append([self.current_pos[2][0], self.current_pos[2][1] - 1])

            # If current direction is West
            else:
                # Return (x-1, y)
                if dist > 0:
                    for i in range(1, dist+1):
                        coord.append([self.current_pos[whichFront][0], self.current_pos[whichFront][1] + i])
                else:
                    coord.append([self.current_pos[0][0], self.current_pos[0][1] + 1])
                    coord.append([self.current_pos[1][0], self.current_pos[1][1] + 1])
                    coord.append([self.current_pos[2][0], self.current_pos[2][1] + 1])

        return coord

    def is_map_complete(self):
        if self.explored_map.sum() == 300:

            return True
        return False

    def is_round_complete(self, start):
        """
        Function to check if map is complete
        :return: Boolean
                True if complete, False otherwise
        """
        # Sum up every element of the matrix
        # If every element is 1, it means that every element is explored and sum should be 300 (15 x 20).
        if self.current_pos[4] == start[4] and self.round == 1:
            for i in range(len(self.explored_map)):
                for j in range(len(self.explored_map[0])):
                    if self.explored_map[i][j] == 0:
                        self.explored_map[i][j] = 1
                        self.real_map[i][j] = 1
            self.save_map(self.explored_map)
            self.save_map(self.real_map)
            self.explore_thread.join()
            #self.update_obstacle_map_thread.join()
            #self.update_explored_map_thread.join()
            return True
        return False

    def reset(self):
        """
        Function to reset all properties to initial state
        :return:
        """
        self.real_map = np.zeros((15, 20))
        self.explored_map = np.zeros((15, 20))
        self.true_start = self.current_pos.copy()

    def check_if_at_point(self, point):
        """
        Function to check if robot is at shifted start
        :return:
        """
        if self.current_pos[4] == point[4]:
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
        front_right_obstacle = round(sensor_data["FrontRight"]/10)
        mid_left_obstacle = round(sensor_data["LeftSide"]/10)

        start_has_obstacle = self.check_obstacle(sensor_data)

        # If there is, update start by 1 in x direction and skip the loop
        if start_has_obstacle:
            print(log_string + text_color.WARNING + 'Obstacle encountered' + text_color.ENDC)
            return -1

        # Check if front has obstacle
        front_obstacle = bool(front_left_obstacle < 2 or front_right_obstacle < 2)

        # If there is an obstacle in front
        if front_obstacle:

            # If there is no obstacle on the left
            if mid_left_obstacle > 3:

                # Update direction
                self.update_dir(True)

                # Tell Arduino to turn left
                return "A1"

            # If there is obstacle in front and no obstacle on right
            else:
                # Update direction
                self.update_dir(False)
                return "D1"

        # If no obstacle in front
        else:
            self.update_pos()
            return "W1"

    def check_obstacle(self, sensor_data):

        front_left_obstacle = round(sensor_data["TopLeft"] / 10)
        front_mid_obstacle = round(sensor_data["TopMiddle"] / 10)
        front_right_obstacle = round(sensor_data["TopRight"] / 10)
        front_coord = self.get_coord('front')

        if self.direction == self.direction.N:
            return bool((front_coord[0][0] + front_left_obstacle) in self.true_start or
                        (front_coord[1][0] + front_mid_obstacle) in self.true_start or
                        (front_coord[2][0] + front_right_obstacle) in self.true_start)
        elif self.direction == self.direction.S:
            return bool((front_coord[0][0] - front_left_obstacle) in self.true_start or
                        (front_coord[1][0] - front_mid_obstacle) in self.true_start or
                        (front_coord[2][0] - front_right_obstacle) in self.true_start)
        elif self.direction == self.direction.E:
            return bool((front_coord[0][1] + front_left_obstacle) in self.true_start or
                        (front_coord[1][1] + front_mid_obstacle) in self.true_start or
                        (front_coord[2][1] + front_right_obstacle) in self.true_start)
        else:
            return bool((front_coord[0][1] - front_left_obstacle) in self.true_start or
                        (front_coord[1][1] - front_mid_obstacle) in self.true_start or
                        (front_coord[2][1] - front_right_obstacle) in self.true_start)

    def set_direction(self, direction):
        if self.direction != direction:
            # Turn left while direction is wrong
            self.move_queue.put("4")
            return False
        return True

    @staticmethod
    def update_start(start, x, y):
        for i in range(len(start)):
            start[i][0] += x
            start[i][1] += y
        return start

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
                temp[j] = temp[j][0]
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
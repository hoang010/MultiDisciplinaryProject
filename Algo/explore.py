import numpy as np
import os
import queue


class Explore:
    def __init__(self, map_size, direction_class):
        """
        Function to initialise an instance of Explore
        :param map_size: Array
                Array containing actual map size
                Should be either (15, 20) or (20, 15)
        :param direction_class: Class
                Class containing directions
        """
        self.direction_class = direction_class
        self.direction = self.direction_class.N
        self.move_queue = queue.Queue()
        self.map_size = map_size
        self.real_map = np.zeros(self.map_size)
        self.explored_map = self.real_map
        self.round = 0
        self.path = (0, 0)

        self.true_start = [(2, 2), (1, 2), (0, 2),
                           (2, 1), (1, 1), (0, 1),
                           (2, 0), (1, 0), (0, 0)]

        self.start = self.true_start

        # Follows format (y, x)
        # If map is (15, 20), i.e. 15 rows x 20 columns then lim(y) = 15, lim(x) = 20,
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
                Array containing sensor data in boolean array
        :return:
        """

        front_left_obstacle = int(sensor_data["TopLeft"])/10
        front_mid_obstacle = int(sensor_data["TopMiddle"])/10
        front_right_obstacle = int(sensor_data["TopRight"])/10
        mid_left_obstacle = int(sensor_data["LeftSide"])/10
        mid_right_obstacle = int(sensor_data["RightSide"])/10
        obstacle_coord = None
        explored_coord = self.current_pos
        right_x, right_y = self.get_coord('right')

        # If there is no obstacle on the right
        if mid_right_obstacle > 2 and self.explored_map[right_x][right_y] == 0:

            movement = '5'

            # Put the command 'right' into queue for main() to read
            self.move_queue.put(movement)

            # Update robot direction
            self.update_dir(left_turn=False)

        # If there is an obstacle in front and on the right
        elif front_left_obstacle < 2 or front_mid_obstacle < 2 or front_right_obstacle < 2:

            movement = '4'

            # Since there is an obstacle on the right, get the coordinates
            right_coord = self.get_coord('right')

            # Check if right side coordinates are within boundaries
            if right_coord[0] >= 0 or right_coord[1] >= 0:
                if right_coord[0] < self.real_map[0] or right_coord[1] < self.real_map[1]:
                    # Add into array for obstacle coordinates
                    obstacle_coord.append(right_coord)

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
            right_coord = self.get_coord('right')

            # Check if right side coordinates are within boundaries
            if right_coord[0] >= 0 or right_coord[1] >= 0:
                if right_coord[0] < self.real_map[0] or right_coord[1] < self.real_map[1]:
                    # Add into array for obstacle coordinates
                    obstacle_coord.append(right_coord)

            movement = '3'

            # Put the command 'advance' into queue for main() to read
            self.move_queue.put(movement)

            self.update_pos()

        # Get left side coordinates
        left_coord = self.get_coord('left')

        # If it is an obstacle, append to array for obstacle
        if mid_left_obstacle:
            obstacle_coord.append(left_coord)

        # Otherwise append to array for explore map
        else:
            explored_coord.append(left_coord)

        # Update map once done
        self.update_map(explored_coord, obstacle_coord)

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
        :param left_turn: Boolean
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
        :param front_left: Boolean
                0 if no obstacle is on front left,
                1 if obstacle is on front left
                should not take any other value
        :param front_mid: Boolean
                0 if no obstacle is on front mid,
                1 if obstacle is on front mid
                should not take any other value
        :param front_right: Boolean
                0 if no obstacle is on front right,
                1 if obstacle is on front right
                should not take any other value
        :return: obstacle: Array
                obstacle coordinates
        """

        obs_bool = [front_left, front_mid, front_right]
        obstacle = []

        for i in range(2, -1, -1):
            if obs_bool[i]:
                # If current direction is North
                if self.direction == self.direction_class.N:
                    # Return (x, y+1)
                    obstacle.append((self.current_pos[i][0], self.current_pos[i][1] + 1))

                # If current direction is South
                elif self.direction == self.direction_class.S:
                    # Return (x, y-1)
                    obstacle.append((self.current_pos[i][0], self.current_pos[i][1] - 1))

                # If current direction is East
                elif self.direction == self.direction_class.E:
                    # Return (x-1, y)
                    obstacle.append((self.current_pos[i][0] - 1, self.current_pos[i][1]))

                # If current direction is West
                else:
                    # Return (x+1, y)
                    obstacle.append((self.current_pos[i][0] + 1, self.current_pos[i][1]))

        return obstacle

    def get_coord(self, direction):

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

        if direction == 'left':
            return left()
        else:
            return right()

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
        if self.current_pos[4] == self.start[4] and self.round == 1:
            return True
        return False

    def update_start(self, x, y):
        for i in range(len(self.start)):
            self.start[i][0] += x
            self.start[i][1] += y
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

import numpy as np
import os
import queue


class Explore:
    # TODO: Add a return to start function
    # TODO: Check if there is enough space to accommodate for a front long range sensor
    # TODO: If enough sensors to be able to put one on the left, use that sensor to explore the left side of robot
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
        self.dir_queue = queue.Queue()
        self.map_size = map_size
        self.real_map = np.zeros(self.map_size)
        self.explored_map = self.real_map

        # (x, y, z):
        #   x = left front obstacle
        #   y = right front obstacle
        #   z = right side obstacle
        self.obstacle = None
        self.path = (0, 0)

        # If map is (15, 20) then coordinates are as follows:
        # (14, 18)[front left], (14, 19)[front right],
        # (13, 18)[back left], (13, 19)[back right]
        # This is done assuming the robot starts at the bottom right of the map wrt numpy array
        self.start = [(len(self.real_map) - 1, len(self.real_map[0]) - 2),
                      (len(self.real_map) - 1, len(self.real_map[0]) - 1),
                      (len(self.real_map) - 2, len(self.real_map[0]) - 1),
                      (len(self.real_map) - 2, len(self.real_map[0]) - 2)]

        self.goal = [(0, 0), (0, 1), (1, 0), (1, 1)]
        self.current_pos = self.start

    def right_wall_hugging(self):
        """
        Function to execute right wall hugging
        :return:
        """

        front_left_obstacle = self.obstacle[0]
        front_right_obstacle = self.obstacle[1]
        right_obstacle = self.obstacle[2]
        obstacle_coord = None

        # If there is no obstacle on the right
        if not right_obstacle:

            # Put the command 'right' into queue for main() to read
            self.dir_queue.put('right')

            # Update robot direction
            self.update_dir(left_turn=False)

        # If there is an obstacle in front and on the right
        elif front_left_obstacle or front_right_obstacle:

            # Get obstacle coordinate
            # If left_obstacle, get obstacle coordinate wrt front left robot coordinate
            # Else get obstacle coordinate wrt front right robot coordinate
            obstacle_coord = self.get_obstacle_coord(0 if front_left_obstacle else 1)

            # Put the command 'left' into queue for main() to read
            self.dir_queue.put('left')

            # Update robot direction
            self.update_dir(left_turn=True)

        # If no obstacle
        else:

            # Put the command 'advance' into queue for main() to read
            self.dir_queue.put('advance')

            # Update robot position
            self.update_pos()

        # Update map once done
        self.update_map(self.current_pos, obstacle_coord)

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

    def get_obstacle_coord(self, left_obstacle):
        """
        Function to get obstacle coordinate
        :param left_obstacle: Integer
                0 if obstacle is on front left,
                1 if obstacle is on front right
                should not take any other value
        :return: obstacle: Array
                obstacle coordinates
        """
        # If current direction is North
        if self.direction == self.direction_class.N:
            # Return (x, y+1)
            obstacle = (self.current_pos[left_obstacle][0], self.current_pos[left_obstacle][1] + 1)

        # If current direction is South
        elif self.direction == self.direction_class.S:
            # Return (x, y-1)
            obstacle = (self.current_pos[left_obstacle][0], self.current_pos[left_obstacle][1] - 1)

        # If current direction is East
        elif self.direction == self.direction_class.E:
            # Return (x-1, y)
            obstacle = (self.current_pos[left_obstacle][0] - 1, self.current_pos[left_obstacle][1])

        # If current direction is West
        else:
            # Return (x+1, y)
            obstacle = (self.current_pos[left_obstacle][0] + 1, self.current_pos[left_obstacle][1])

        return obstacle

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

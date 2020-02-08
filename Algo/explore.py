import numpy as np
import os
import queue


class Explore:
    def __init__(self, map_size, direction_class):
        self.direction_class = direction_class
        self.direction = self.direction_class.N
        self.dir_queue = queue.Queue()
        self.real_map = np.zeros(map_size)
        self.explored_map = self.real_map

        # For go_to_min algo
        self.min_coord = None

        # (x, y, z):
        #   x = left front obstacle
        #   y = right front obstacle
        #   z = right side obstacle
        self.obstacle = None
        self.path = (0, 0)
        self.start = [(len(self.real_map) - 1, len(self.real_map[0]) - 1),
                      (len(self.real_map) - 1, len(self.real_map[0]) - 2),
                      (len(self.real_map) - 2, len(self.real_map[0]) - 1),
                      (len(self.real_map) - 2, len(self.real_map[0]) - 2)]

        # TODO: Not sure about this, how to update?
        self.goal = (0, 0)
        self.current_pos = self.start

    def right_wall_hugging(self):

        front_left_obstacle = self.obstacle[0]
        front_right_obstacle = self.obstacle[1]
        right_obstacle = self.obstacle[2]
        obstacle_coord = None

        # If there is no obstacle on the right
        if not right_obstacle:

            # Put the command 'right' into queue for main() to read
            self.dir_queue.put('right')

            # Update robot direction
            self.right_update_dir()

        # If there is an obstacle in front
        elif front_left_obstacle or front_right_obstacle:

            # Get obstacle coordinate
            # If left_obstacle, get obstacle coordinate wrt front left robot coordinate
            # Else get obstacle coordinate wrt front right robot coordinate
            obstacle_coord = self.get_obstacle_coord(0 if front_left_obstacle else 1)

            # Put the command 'left' into queue for main() to read
            self.dir_queue.put('left')

            # Update robot direction
            self.left_update_dir()

        # If no obstacle
        else:

            # Put the command 'advance' into queue for main() to read
            self.dir_queue.put('advance')

            # Update robot position
            self.update_pos()

        # Update map once done
        self.update_map(self.current_pos, obstacle_coord)

    def update_pos(self):
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
        for x, y in coord_array:
            self.explored_map[x][y] = 1

        if obstacle:
            for x, y in obstacle:
                self.real_map[x][y] = 1

    def left_update_dir(self):
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

    def right_update_dir(self):
        # If current direction is North, North turning to left is East
        if self.direction == self.direction_class.N:
            # Change current direction to East
            self.direction = self.direction_class.E

        # If current direction is South, North turning to left is West
        elif self.direction == self.direction_class.S:
            # Change current direction to West
            self.direction = self.direction_class.W

        # If current direction is East, North turning to left is North
        elif self.direction == self.direction_class.E:
            # Change current direction to North
            self.direction = self.direction_class.N

        # If current direction is West, North turning to left is South
        else:
            # Change current direction to South
            self.direction = self.direction_class.S

    def get_obstacle_coord(self, left_obstacle):
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
        if self.explored_map.sum() == 300:
            self.save_map(self.explored_map)
            self.save_map(self.real_map)
            return True
        return False

    def reset(self):
        self.real_map = np.zeros((20, 15))
        self.explored_map = np.zeros((20, 15))
        self.path = (0, 0)
        self.start = (0, 0)
        self.goal = (0, 0)
        self.current_pos = self.start

    @staticmethod
    def save_map(hex_map):
        directory = './Maps'

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

        hex_array = []
        hex_map = ''
        for i in range(len(bin_map)):
            temp = bin_map[i].astype(str).tolist()
            for j in range(len(bin_map[i])):
                temp = temp[j][-1]
            temp = ''.join(temp)
            hex_array.append(temp)
        hex_array = '11' + ''.join(hex_array) + '11'
        for i in range(0, len(hex_array), 8):
            j = 1 + 8
            hex_map += hex(int(hex_array[i:j], 2))[2:].zfill(2)
        return hex_map

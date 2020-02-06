import numpy as np
import os


class Explore:
    def __init__(self):
        self.real_map = np.zeros((20, 15))
        self.explored_map = np.zeros((20, 15))
        self.path = (0, 0)
        self.start = (0, 0)
        self.goal = (0, 0)
        self.current_pos = self.start
        print(self.real_map)
        print(self.current_pos)

    # def scan(self):

    # def decide(self):

    # def move(self):

    def update_map(self, coord_array, obstacle):
        # TODO: coord_array and obstacle are to be an array of coordinates, i.e. [[x1, y1], [x2, y2]]
        for x, y in coord_array:
            self.explored_map[x][y] = 1

        for x, y in obstacle:
            self.real_map[x][y] = 1

    def is_map_complete(self):

        # If all the bits are 1
        if self.explored_map.sum() == 300:

            directory = './Maps'

            if not os.path.exists(directory):
                os.makedirs(directory)

            # Get number of files already in Maps sub-folder
            num = len([name for name in os.listdir(directory) if os.path.isfile(name)])

            # Open/Create a file with Map <num>.txt
            f = open(directory + 'Map {}.txt'.format(num), 'w+')

            # For each row in self.explored_map
            for i in range(self.explored_map.size()):

                # Combine all elements in each row (as an array) into one string
                self.explored_map[i] = ''.join(self.explored_map[i])

                # Save it to the opened file
                f.write('{}\n'.format(self.explored_map[i]))

                # Combine all elements in each row (as an array) into one string
                self.real_map[i] = ''.join(self.real_map[i])

            # Close the file
            f.close()

            # Add '11' before and after as required
            explored_bin_str = '11' + ''.join(self.explored_map) + '11'
            real_bin_str = '11' + ''.join(self.real_map) + '11'

            # Convert strings to hexadecimal
            explored_hex_str = hex(int(explored_bin_str, 2))[1:]
            real_hex_str = hex(int(real_bin_str, 2))[1:]

            # Return the hexadecimal strings
            return real_hex_str, explored_hex_str

        return None, None

    def reset(self):
        self.real_map = np.zeros((20, 15))
        self.explored_map = np.zeros((20, 15))
        self.path = (0, 0)
        self.start = (0, 0)
        self.goal = (0, 0)
        self.current_pos = self.start

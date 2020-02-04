import numpy as np


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
        if self.explored_map.sum() == 300:
            for i in range(self.explored_map.size()):
                self.explored_map[i] = ''.join(self.explored_map[i])
                self.real_map[i] = ''.join(self.real_map[i])

            explored_bin_str = '11' + ''.join(self.explored_map) + '11'
            real_bin_str = '11' + ''.join(self.real_map) + '11'

            explored_hex_str = hex(int(explored_bin_str, 2))[1:]
            real_hex_str = hex(int(real_bin_str, 2))[1:]
            return real_hex_str, explored_hex_str
        return False

    def reset(self):
        self.real_map = np.zeros((20, 15))
        self.explored_map = np.zeros((20, 15))
        self.path = (0, 0)
        self.start = (0, 0)
        self.goal = (0, 0)
        self.current_pos = self.start

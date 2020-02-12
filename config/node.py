

class Node:
    def __init__(self, prev_node, node_dir, current_cost, pos, goal):
        """
        Function to init a Node
        :param prev_node: Array
                Array containing coordinates of previous position
        :param node_dir: Direction
                Direction the node can be facing
        :param current_cost: int
                Integer representing how much cost has been incurred up to current position
        :param pos: Array
                Array containing coordinates of current position
        :param goal: Array
                Array containing coordinates of goal position
        """
        self.prev_node = prev_node
        self.ref_pt = (pos[0][0], pos[0][1])
        self.gx = current_cost
        self.pos = pos
        self.goal = goal
        self.hx = self.heuristic_fn()
        self.dir = node_dir
        self.next_coord = []

    def get_next_coord(self):
        # If direction is facing North, then previous coordinate must be 1y up
        north_coord = [(self.pos[0][0], self.pos[0][1] - 1),
                      (self.pos[1][0], self.pos[1][1] - 1),
                      (self.pos[2][0], self.pos[2][1] - 1),
                      (self.pos[3][0], self.pos[3][1] - 1)]

        # Otherwise direction must be facing East, then previous coordinate must be 1x up
        east_coord = [(self.pos[0][0] - 1, self.pos[0][1]),
                      (self.pos[1][0] - 1, self.pos[1][1]),
                      (self.pos[2][0] - 1, self.pos[2][1]),
                      (self.pos[3][0] - 1, self.pos[3][1])]

        self.next_coord = [north_coord, east_coord]

    def heuristic_fn(self):
        """
        Function to calculate heuristic function of Node
        Currently, heuristic function of Node is taken to be the shortest DIRECT path to goal
        instead of accounting for obstacles

        :return: Manhattan distance
        """
        # Get x and y values of top right corner of goal
        goal_x = self.goal[0][0]
        goal_y = self.goal[0][1]

        # Get x and y values of top right of current position
        start_x = self.ref_pt[0]
        start_y = self.ref_pt[1]

        return start_x - goal_x, start_y - goal_y

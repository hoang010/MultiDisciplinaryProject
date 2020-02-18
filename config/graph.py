class Graph:
    class Node:
        def __init__(self, current_cost, pos, goal, prev_node=None):
            """
            Function to init a Node
            :param node_dir: Direction
                    Direction the node can be facing
            :param current_cost: int
                    Integer representing how much cost has been incurred up to current position
            :param pos: Array
                    Array containing coordinates of current position
            :param goal: Array
                    Array containing coordinates of goal position
            :param prev_node: Node
                    Parent Node
            """
            self.parent = prev_node
            self.ref_pt = (pos[0], pos[1])
            self.pos = pos
            self.goal = goal
            self.next_coord = []
            self.hx = self.heuristic_fn()
            self.gx = current_cost
            self.fx = self.gx + self.hx

        def heuristic_fn(self):
            """
            Function to calculate heuristic function of Node
            Currently, heuristic function of Node is taken to be the shortest DIRECT path to goal
            instead of accounting for obstacles

            :return: Manhattan distance
            """
            # Get x and y values of top right corner of goal
            goal_x = self.goal[4][0]
            goal_y = self.goal[4][1]

            # Get x and y values of top right of current position
            start_x = self.ref_pt[0]
            start_y = self.ref_pt[1]

            return start_x - goal_x, start_y - goal_y

        @staticmethod
        def search_near(cost, x, y, node):
            near_node = Graph.Node(cost+1, (node.ref_pt[0] + x, node.ref_pt[1] + y), node)
            return near_node

    def __init__(self, real_map, goal):
        """
        Function to init a Graph
        :param real_map: Array
                Array containing numpy representation of real map
        """
        self.path = []
        self.visited = []
        self.to_visit = []
        self.real_map = (real_map[0] - 1, real_map[1] -1)
        self.goal = goal
        self.goal_ref_pt = (goal[4][0], goal[4][1])
        self.to_visit.append(Graph.Node(0, (0, 0), self.goal_ref_pt))
        # cost = 0
        #
        # # For each row (y)
        # for y in range(len(self.real_map) - 1):
        #     # For each column (x)
        #     for x in range(len(self.real_map[y]) - 1):
        #         if self.real_map[x][y] != 1:
        #             self.to_visit.append(Graph.Node(cost, (x, y), goal))
        #         cost += 1
        #     cost = y + 1

    def check_visited(self, node):
        if node in self.visited:
            return True
        return False

    def check_not_visited(self, node):
        if node in self.to_visit:
            return node
        return False

    def check_nearby(self, node):
        ud = [1, -1, 0, 0, 1, 1, -1, -1]
        rl = [0, 0, 1, -1, 1, -1, 1, -1]

        coord = list(zip(ud, rl))

        for x, y in coord:
            node_temp = node.search_near(node.gx, x, y, node)

            if node_temp.ref_pt == self.goal_ref_pt:
                return 1
            elif self.check_visited(node_temp):
                pass
            elif not self.check_not_visited(node_temp):
                node_temp.father = node
                self.to_visit.append(node_temp)
            else:
                if node_temp.fx < self.check_not_visited(node_temp).fx:
                    self.to_visit.remove(self.check_not_visited(node_temp))
                    node_temp.parent = node
                    self.to_visit.append(node_temp)

    def find_path(self):
        for node in self.to_visit:
            self.check_nearby(node)


    @staticmethod
    def convert_string_to_coord(string):
        """
        Function to convert dictionary key back into coordinate
        :param string: String
                String containing coordinates of reference point in String
        :return: coord: Array
                Array containing reference coordinate of node
        """
        # Initialise coordinate Array
        coord = ['', '']

        # Initialise required index for coordinate array
        j = 0

        # Add each element of string into coordinate Array as string
        # If separator (,) is added, remove it and increment index j
        for i in range(len(string)):
            coord[j] += string[i]
            if string[i] == ',':
                coord[j] = coord[j][:-1]
                j += 1

        # Convert String to Integer
        coord = (int(coord[0]), int(coord[1]))
        return coord

    @staticmethod
    def convert_coord_to_string(coord):
        """
        Function to convert coordinated into dictionary key
        :param coord: Array
                Array containing reference coordinate of node
        :return: string: String
                String containing coordinates of reference point in String
        """
        # Initialise key
        string = ''

        # Add element into key as string
        # If (15, 20) is passed, this function should return 15,20 as key
        for i in range(len(coord)):
            string += str(coord[i])
            if i == 0:
                string += ','
        return string

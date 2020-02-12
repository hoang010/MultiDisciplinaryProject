class Graph:
    def __init__(self, real_map):
        """
        Function to init a Graph
        :param real_map: Array
                Array containing numpy representation of real map
        """
        self.real_map = real_map
        self.graph = {}

    def complete(self):
        """
        Function to check if graph has (300 - length of real_map) unique nodes
        :return: boolean
                True if complete, False otherwise
        """
        unique_ref_pt = []
        for key, value in self.graph.items():
            unique_ref_pt.append(key)
            for item in value:
                unique_ref_pt.append(item)

        num_of_nodes = len(set(unique_ref_pt))

        # There is one whole column in which the reference point will not reach,
        # hence remove one whole columns' worth
        if num_of_nodes != (300 - len(self.real_map)):
            return False
        return True

    def update(self, node):
        """
        Function to update graph given a node
        :param node: Node
                Node containing properties of a certain location in real map
        :return: Int
                1 if added, -1 otherwise
        """
        # For every (x, y) in node, check if it is an obstacle or if it exceeds map dimensions
        # If it is, return -1 to tell main to display message accordingly
        for x, y in node:
            if x < 0 or y < 0 or self.real_map[x][y] == 1:
                return -1

        # If node does not overlap with an obstacle, convert reference point into key
        graph_key = self.convert_coord_to_string(node.prev_node.ref_pt)

        # Append node using reference point as key
        if graph_key not in self.graph.keys():
            self.graph[graph_key] = [node]

        else:
            self.graph[graph_key].append(node)

        # Return 1 to tell main to display message accordingly
        return 1

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

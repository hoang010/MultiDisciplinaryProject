import sys
# point in the map


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return 1
        else:
            return 0


# create map using list
class Map2d:
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.data = []
        self.data = [[0 for i in range(width)] for j in range(height)]

    def map_show(self):
        for i in range(self.height):
            for j in range(self.width):
                print(self.data[i][j], end=' ')
            print("")

    def obstacle(self, obstacle_x, obstacle_y):
        self.data[obstacle_x][obstacle_y] = 1

    def end_draw(self, point):
        self.data[point.x][point.y] = 6


# A* algorithm
class AStar:
    # set all nodes
    class Node:
        def __init__(self, point, endpoint, g):
            self.point = point  # own coords
            self.endpoint = endpoint  # own coords
            self.father = None  # parent node
            self.g = g  # g value，will calculate again when using
            self.h = (abs(endpoint.x - point.x) + abs(endpoint.y - point.y)) * 10  # calculating h value
            self.f = self.g + self.h

        # find nearby nodes
        def search_near(self, ud, rl):  # up  down  right left
            near_point = Point(self.point.x + rl, self.point.y + ud)
            near_node = AStar.Node(near_point, self.endpoint, self.g + 1)
            return near_node

    def __init__(self, start_point, end_point, map):  # pass to class
        self.path = []
        self.close_list = []  # store visited node
        self.open_list = []  # store to-visit node
        self.current = 0  # current node
        self.start_point = start_point
        self.end_point = end_point
        self.map = map  # current map

    def select_current(self):
        min = 10000000
        node_temp = 0
        for ele in self.open_list:
            if ele.f < min:
                min = ele.f
                node_temp = ele
        self.path.append(node_temp)
        self.open_list.remove(node_temp)
        self.close_list.append(node_temp)
        return node_temp

    def is_in_open_list(self, node):
        for open_node_temp in self.open_list:
            if open_node_temp.point == node.point:
                return open_node_temp
        return 0

    def is_in_close_list(self, node):
        for close_node_temp in self.close_list:
            if close_node_temp.point == node.point:
                return 1
        return 0

    def is_obstacle(self, node):
        if self.map.data[node.point.x][node.point.y] == 1:
            return 1
        return 0

    def near_explore(self, node):
        ud = [1, -1, 0, 0, 1, 1, -1, -1]
        rl = [0, 0, 1, -1, 1, -1, 1, -1]

        coord = list(zip(ud, rl))

        for item in coord:
            node_temp = node.search_near(item[0], item[1])
            if node_temp.point == self.end_point:
                return 1
            elif self.is_in_close_list(node_temp):
                pass
            elif self.is_obstacle(node_temp):
                pass
            elif self.is_in_open_list(node_temp) == 0:
                node_temp.father = node
                self.open_list.append(node_temp)
            else:
                if node_temp.f < (self.is_in_open_list(node_temp)).f:
                    self.open_list.remove(self.is_in_open_list(node_temp))
                    node_temp.father = node
                    self.open_list.append(node_temp)

        return 0

## build map, it's just a demo. obstacle is put at random
# ss=Map2d(10,20)
# for i in range(10):
#     ss.obstacle(4, i)
# for i in range(19):
#     ss.obstacle(0, i+1)
# for i in range(9):
#     ss.obstacle(i+1, 0)
# for i in range(9):
#     ss.obstacle(i+1, 19)
# for i in range(19):
#     ss.obstacle(9, i)
# ss.obstacle(8, 6)
# ss.obstacle(6, 8)
# ss.obstacle(6, 15)
# ss.obstacle(9, 10)
# start_point = Point(1, 2)
# end_point = Point(9, 19)
# ss.end_draw(end_point)
# ss.end_draw(start_point)
#
# # init A*
# a_star = AStar(start_point, end_point, ss)
# start_node = a_star.Node(start_point, end_point, 0)
# a_star.open_list.append(start_node)
#
# flag = 0  # reach the goal
# m = 0  # steps count
#
# # searching loop
# while flag != 1:
#     a_star.current = a_star.select_current()  # choose one node from open_list
#     flag = a_star.near_explore(a_star.current)  # search nearby node of current node
#     m = m+1
#     print(m)
#
# # draw map
# for node_path in a_star.path:
#     ss.end_draw(node_path.point)
# ss.map_show()

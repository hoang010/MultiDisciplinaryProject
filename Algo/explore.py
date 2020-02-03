class Explore:
    def __init__(self):
        self.real_map = (0, 0)
        self.path = (0, 0)
        self.start = (0, 0)
        self.goal = (0, 0)
        self.current_pos = self.start
        print(self.real_map)
        print(self.current_pos)

    # def scan(self):

    # def decide(self):

    # def move(self):

    def is_map_complete(self):
        if self.real_map[0] == (20, 20):
            return True
        return False

    def reset(self):
        self.real_map = (0, 0)
        self.path = (0, 0)
        self.start = (0, 0)
        self.goal = (0, 0)
        self.current_pos = self.start

class Widget:
    name = "Rectangle of Glory"
    default_size = [5, 5]
    max_size = None
    min_size = None
    desired_spf = 60

    current_size = default_size
    def get_frame(self):
        return [[255] * self.current_size[0] for _ in range(0, self.current_size[1])]
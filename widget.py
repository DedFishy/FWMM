class Widget:
    name = None
    default_size = None
    max_size = None
    min_size = None
    desired_spf = None

    current_size = default_size
    def get_frame(self):
        return [[255] * self.current_size[0] for _ in range(0, self.current_size[1])]
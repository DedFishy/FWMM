from enum import Enum

class WidgetRotation(Enum):
    NORTH = 0
    SOUTH = 1
    EAST = 2
    WEST = 3

class Widget:
    name: str = None
    default_size = None
    max_size = None
    min_size = None
    desired_spf = None
    position = [0,0]
    rotation = WidgetRotation.NORTH

    current_size = default_size
    def get_frame(self):
        return [[255] * self.current_size[0] for _ in range(0, self.current_size[1])]
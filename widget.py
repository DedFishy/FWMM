import numpy as np
from widget_config_item import WidgetConfigItem


class Widget:
    """Base class for widgets"""
    name: str = "Unnamed"
    position = [0,0]
    rotation = 0 # Must be 0 or multiple of 90
    import_name = "Unnamed"
    allow_rotation = True

    configuration: dict[str, WidgetConfigItem] = {}

    def __init__(self):
        self.position = [0,0]

    def get_current_size(self):
        """Get the size of the widget in pixels"""
        return [0,0]

    def get_desired_spf(self):
        """Get how quickly the widget should update in seconds per frame"""
        return -1

    def get_frame(self) -> np.matrix | list[list[int]]:
        """Return the current frame as a numpy matrix or a 2D array"""
        return [[255] * self.current_size[0] for _ in range(0, self.current_size[1])] # type: ignore
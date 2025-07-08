from enum import Enum

from widget_config_item import WidgetConfigItem


class Widget:
    name: str = "Unnamed"
    position = [0,0]
    rotation = 0 # Must be 0 or multiple of 90
    import_name = None
    allow_rotation = True

    configuration: dict[str, WidgetConfigItem] = {}

    def __init__(self):
        self.position = [0,0]

    def get_current_size(self):
        return [0,0]

    def get_desired_spf(self):
        return -1

    def get_frame(self):
        return [[255] * self.current_size[0] for _ in range(0, self.current_size[1])]
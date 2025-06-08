from enum import Enum

from widget_config_item import WidgetConfigItem


class Widget:
    name: str = None
    position = [0,0]
    rotation = 0 # Each increment from 0 is 90 degrees clockwise
    import_name = None

    configuration: dict[str, WidgetConfigItem] = {}

    def get_current_size(self):
        return [0,0]

    def get_desired_spf(self):
        return -1

    def get_frame(self):
        return [[255] * self.current_size[0] for _ in range(0, self.current_size[1])]
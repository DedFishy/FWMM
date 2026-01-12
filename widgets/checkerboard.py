from datetime import datetime
from widget import Widget as WidgetBase
from widget_config_item import WidgetConfigItem as Config
from widget_config_item import ConfigItemType as ConfigType
from const import WIDTH, HEIGHT
import numpy as np

class Widget(WidgetBase):
    name = "Checkerboard"
    desired_spf = -1
    allow_rotation = False

    start_time = datetime.now().timestamp()

    def __init__(self):
        super().__init__()
        self.configuration = {
            "Board Width": Config(ConfigType.integer, 5, 1, WIDTH),
            "Board Height": Config(ConfigType.integer, 5, 1, HEIGHT),
            "Brightness 1": Config(ConfigType.integer, 255, 0, 255),
            "Brightness 2": Config(ConfigType.integer, 0, 0, 255),
            "Board Size": Config(ConfigType.integer, 1, 1, WIDTH),
            "X Offset": Config(ConfigType.integer, 0, -10, WIDTH),
            "Y Offset": Config(ConfigType.integer, 0, -10, HEIGHT),
            "Time Between Updates (sec)": Config(ConfigType.integer, -1, -1, 30),
            "X Speed (px per s)": Config(ConfigType.integer, 0, -10, 10),
            "Y Speed (px per s)": Config(ConfigType.integer, 0, -10, 10)
        }

    def get_current_size(self):
        return [self.configuration["Board Width"].value, self.configuration["Board Height"].value]
    
    def get_desired_spf(self):
        return self.configuration["Time Between Updates (sec)"].value

    def get_frame(self):
        width = self.configuration["Board Width"].value
        height = self.configuration["Board Height"].value
        size = self.configuration["Board Size"].value

        xspeed = self.configuration["X Speed (px per s)"].value
        yspeed = self.configuration["Y Speed (px per s)"].value

        delta_time = float(datetime.now().timestamp() - self.start_time)

        xoff = self.configuration["X Offset"].value + int(xspeed * delta_time) % (size << 1)
        yoff = self.configuration["Y Offset"].value + int(yspeed * delta_time) % (size << 1)

        base = np.matrix([[ self.configuration["Brightness 1"].value if ( (((x - xoff) // size) % 2) + (((y - yoff) // size) % 2) != 1 ) else self.configuration["Brightness 2"].value for x in range(width)] for y in range(height)]) # type: ignore

        return base

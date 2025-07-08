import util
from widget import Widget as WidgetBase
from widget_config_item import WidgetConfigItem as Config
from widget_config_item import ConfigItemType as ConfigType
from const import WIDTH, HEIGHT
import plyer
import numpy as np

class Widget(WidgetBase):
    name = "Bar"
    desired_spf = -1
    allow_rotation = True

    fill_sources = {
        "None": lambda w: 0,
        "Battery": lambda w: plyer.battery.status["percentage"]/100, # type: ignore
    }

    def __init__(self):
        super().__init__()
        self.configuration = {
            "Width": Config(ConfigType.integer, 5, 1, max(WIDTH, HEIGHT)),
            "Height": Config(ConfigType.integer, 5, 1, max(WIDTH, HEIGHT)),
            "Border Thickness": Config(ConfigType.integer, 1, 0, 40),
            "Border Brightness": Config(ConfigType.integer, 255, 0, 255),
            "Brightness": Config(ConfigType.integer, 255, 0, 255),
            "Time Between Updates (sec)": Config(ConfigType.integer, -1, -1, 30),
            "Fill Source": Config(ConfigType.combo, "None", options=list(self.fill_sources.keys()))
        }

    def get_current_size(self):
        return [self.configuration["Width"].value, self.configuration["Height"].value]
    
    def get_desired_spf(self):
        return self.configuration["Time Between Updates (sec)"].value

    def get_frame(self):
        width = self.configuration["Width"].value
        height = self.configuration["Height"].value

        fill = self.fill_sources[self.configuration["Fill Source"].value](self)
        print(fill)
        max_width = fill * width
        #print(max_width)
        base = np.matrix([[int(max_width > x) * self.configuration["Brightness"].value for x in range(width)] for _ in range(height)])

        border_thickness = self.configuration["Border Thickness"].value
        border_brightness = self.configuration["Border Brightness"].value
        base[:, 0:border_thickness] = border_brightness
        base[:, width-border_thickness:width] = border_brightness
        base[0:border_thickness, :] = border_brightness
        base[height-border_thickness:height, :] = border_brightness
        
        return base

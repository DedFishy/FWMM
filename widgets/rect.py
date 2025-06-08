from widget import Widget as WidgetBase
from widget_config_item import WidgetConfigItem as Config
from widget_config_item import ConfigItemType as ConfigType
from const import WIDTH, HEIGHT

class Widget(WidgetBase):
    name = "Rectangle of Glory"
    desired_spf = 60

    def __init__(self):
        self.configuration = {
            "Rectangle Width": Config(ConfigType.integer, 5, 1, WIDTH),
            "Rectangle Height": Config(ConfigType.integer, 5, 1, HEIGHT),
            "Brightness": Config(ConfigType.integer, 255, 0, 255)
        }

    def get_current_size(self):
        return [self.configuration["Rectangle Width"].value, self.configuration["Rectangle Height"].value]
    
    def get_desired_spf(self):
        return -1

    def get_frame(self):
        return [[self.configuration["Brightness"].value] * self.get_current_size()[0] for _ in range(0, self.get_current_size()[1])]
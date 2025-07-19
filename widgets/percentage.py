from text_based_widget import TextBasedWidget
from widget_config_item import WidgetConfigItem as Config
from widget_config_item import ConfigItemType as ConfigType
from font_loader import get_fonts
import psutil

battery = psutil.sensors_battery()

class Widget(TextBasedWidget):
    name = "Percentage"

    percentage_sources = {
        "None": lambda w: 0,
        "Battery": lambda w: battery.percent,
        "CPU Usage": lambda w: psutil.cpu_percent(0),
        "RAM Usage": lambda w: psutil.virtual_memory().percent
    }

    def __init__(self):
        super().__init__()
        self.configuration = {
            "Brightness": Config(ConfigType.integer, 255, 0, 255),
            "Font": Config(ConfigType.combo, get_fonts()[0], options=get_fonts()),
            "Percentage Source": Config(ConfigType.combo, "Battery", options=list(self.percentage_sources.keys())),
            "Text Spacing": Config(ConfigType.integer, 1, 0, 10),
            "Show Percent Symbol": Config(ConfigType.boolean, False)
        }

    def get_brightness(self):
        return self.configuration["Brightness"].value
    def get_font(self):
        return self.configuration["Font"].value
    def get_spacing(self):
        return self.configuration["Text Spacing"].value
    def get_text(self):
        print(self.configuration["Percentage Source"].value, self.configuration["Show Percent Symbol"].value)
        return str(int(self.percentage_sources[self.configuration["Percentage Source"].value](self))) + ("%" if self.configuration["Show Percent Symbol"].value else "")
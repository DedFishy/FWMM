from datetime import datetime
from text_based_widget import TextBasedWidget
import util
from widget import Widget as WidgetBase
from widget_config_item import WidgetConfigItem as Config
from widget_config_item import ConfigItemType as ConfigType
from const import WIDTH, HEIGHT
import numpy as np
from font_loader import load_preloaded_font, get_fonts

class Widget(TextBasedWidget):
    name = "Clock"

    def __init__(self):
        super().__init__()
        self.configuration = {
            "Brightness": Config(ConfigType.integer, 255, 0, 255),
            "Font": Config(ConfigType.combo, get_fonts()[0], options=get_fonts()),
            "Digit Spacing": Config(ConfigType.integer, 1, 0, 10),
            "Twelve Hour": Config(ConfigType.boolean, True)
        }
    
    def get_desired_spf(self):
        return 30
    def get_brightness(self):
        return self.configuration["Brightness"].value
    def get_font(self):
        return self.configuration["Font"].value
    def get_spacing(self):
        return self.configuration["Digit Spacing"].value
    
    def get_text(self):
        digit_one = 0
        digit_two = 0
        digit_three = 0
        digit_four = 0
        current_time = datetime.now()
        hour = current_time.hour
        if self.configuration["Twelve Hour"].value:
            hour = self.twentyfour_to_twelve(hour)
        hour = str(hour)
        if len(hour) == 1: digit_two = int(hour)
        else: 
            digit_one = hour[0]
            digit_two = hour[1]

        minute = str(current_time.minute)
        if len(minute) == 1: digit_four = int(minute)
        else: 
            digit_three = minute[0]
            digit_four = minute[1]
        return f"{digit_one}{digit_two}:{digit_three}{digit_four}"

    def twentyfour_to_twelve(self, hour):
        if hour / 12 > 1:
            return hour - 12
        return hour
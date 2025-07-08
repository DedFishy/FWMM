from datetime import datetime
import util
from widget import Widget as WidgetBase
from widget_config_item import WidgetConfigItem as Config
from widget_config_item import ConfigItemType as ConfigType
from const import WIDTH, HEIGHT
import numpy as np
from font_loader import load_preloaded_font, get_fonts


class Widget(WidgetBase):
    name = "Clock"
    allow_rotation = True
    current_render: np.matrix = np.matrix([[]])
    rotation = 0
    font = None
    loaded_font_name = None

    def __init__(self):
        super().__init__()
        self.configuration = {
            "Brightness": Config(ConfigType.integer, 255, 0, 255),
            "Twelve Hour": Config(ConfigType.boolean, False),
            "Font": Config(ConfigType.combo, "Medium", options=get_fonts())
        }

    def get_current_size(self):
        return [self.current_render.shape[1], self.current_render.shape[0]]
    
    def get_desired_spf(self):
        return 30
    
    def append_character(self, matrix: np.matrix, character: np.matrix, spacing=1):
        spacer = [
            [0 for _ in range(0, spacing)] for _ in range(0, matrix.shape[0])
        ]
        matrix = np.concatenate((matrix, np.matrix(spacer)), axis=1) # type: ignore
        matrix = np.concatenate((matrix, character), axis=1) # type: ignore
        return matrix
    
    def render(self, digit_one, digit_two, digit_three, digit_four):
        if self.font == None or self.loaded_font_name != self.configuration["Font"].value:
            self.loaded_font_name = self.configuration["Font"].value
            self.font = load_preloaded_font(self.loaded_font_name)
        rows = np.matrix([
            [] for _ in range(0, self.font.get_char_height())
        ])
        rows = self.append_character(rows, self.font[digit_one], spacing=0)
        rows = self.append_character(rows, self.font[digit_two])
        rows = self.append_character(rows, self.font[":"])
        rows = self.append_character(rows, self.font[digit_three])
        rows = self.append_character(rows, self.font[digit_four])
        for y in range(0, len(rows)):
            for x in range(0, len(rows[y])):
                rows[y][x] *= self.configuration["Brightness"].value
        self.current_render = rows
        return rows

    def twentyfour_to_twelve(self, hour):
        if hour / 12 > 1:
            return hour - 12
        return hour

    def get_frame(self):
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
        return self.render(digit_one, digit_two, digit_three, digit_four)
from datetime import datetime
from widget import Widget as WidgetBase
from widget_config_item import WidgetConfigItem as Config
from widget_config_item import ConfigItemType as ConfigType
from const import WIDTH, HEIGHT
import numpy as np

numbers = [
np.matrix([
    [1,1,1],
    [1,0,1],
    [1,0,1],
    [1,0,1],
    [1,1,1],
]),
np.matrix([
    [1],
    [1],
    [1],
    [1],
    [1],
]),
np.matrix([
    [1,1,1],
    [0,0,1],
    [1,1,1],
    [1,0,0],
    [1,1,1],
]),
np.matrix([
    [1,1,1],
    [0,0,1],
    [0,1,1],
    [0,0,1],
    [1,1,1],
]),
np.matrix([
    [1,0,1],
    [1,0,1],
    [1,1,1],
    [0,0,1],
    [0,0,1],
]),
np.matrix([
    [1,1,1],
    [1,0,0],
    [1,1,1],
    [0,0,1],
    [1,1,1],
]),
np.matrix([
    [1,1,1],
    [1,0,0],
    [1,1,1],
    [1,0,1],
    [1,1,1],
]),
np.matrix([
    [1,1,1],
    [0,0,1],
    [0,0,1],
    [0,0,1],
    [0,0,1],
]),
np.matrix([
    [1,1,1],
    [1,0,1],
    [1,1,1],
    [1,0,1],
    [1,1,1],
]),
np.matrix([
    [1,1,1],
    [1,0,1],
    [1,1,1],
    [0,0,1],
    [1,1,1],
]),
]
colon = np.matrix([
    [0],
    [1],
    [0],
    [1],
    [0],
])

class Widget(WidgetBase):
    name = "Clock"
    desired_spf = 60
    allow_rotation = True
    current_render = [[]]

    def __init__(self):
        self.configuration = {
            "Brightness": Config(ConfigType.integer, 255, 0, 255),
            "Is Twelve Hour (0/1)": Config(ConfigType.integer, 0, 0, 1)
        }

    def get_current_size(self):
        return [len(self.current_render[0]), len(self.current_render)]
    
    def get_desired_spf(self):
        return -1
    
    def append_character(self, matrix: np.matrix, character: np.matrix, spacing=1):
        matrix = np.concatenate(matrix, character) # TODO: Finish conversion to Numpy, add rotation to the transform list, and add configuration types for booleans and dropdowns (index based)
        return matrix
    
    def render(self, digit_one, digit_two, digit_three, digit_four):
        rows = np.matrix([
            [],
            [],
            [],
            [],
            []
        ])
        rows = self.append_character(rows, numbers[digit_one])
        rows = self.append_character(rows, numbers[digit_two])
        rows = self.append_character(rows, colon)
        rows = self.append_character(rows, numbers[digit_three])
        rows = self.append_character(rows, numbers[digit_four])
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
        if self.configuration["Is Twelve Hour (0/1)"].value:
            hour = self.twentyfour_to_twelve(hour)
        hour = str(hour)
        if len(hour) == 1: digit_two = int(hour)
        else: 
            digit_one = int(hour[0])
            digit_two = int(hour[1])

        minute = str(current_time.minute)
        if len(minute) == 1: digit_four = int(minute)
        else: 
            digit_three = int(minute[0])
            digit_four = int(minute[1])
        return self.render(digit_one, digit_two, digit_three, digit_four)
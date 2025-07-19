from datetime import datetime
import util
from widget import Widget as WidgetBase
from widget_config_item import WidgetConfigItem as Config
from widget_config_item import ConfigItemType as ConfigType
from const import WIDTH, HEIGHT
import numpy as np
from font_loader import load_preloaded_font, get_fonts


class Widget(WidgetBase):
    name = "Text"
    allow_rotation = True
    current_render: np.matrix = np.matrix([[]])
    rotation = 0
    font = None
    loaded_font_name = None

    def __init__(self):
        super().__init__()
        self.configuration = {
            "Brightness": Config(ConfigType.integer, 255, 0, 255),
            "Font": Config(ConfigType.combo, "Medium", options=get_fonts()),
            "Text": Config(ConfigType.text, "Text"),
            "Letter Spacing": Config(ConfigType.integer, 1, 0, 10),

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
    
    def render(self,):
        if self.font == None or self.loaded_font_name != self.configuration["Font"].value:
            self.loaded_font_name = self.configuration["Font"].value
            self.font = load_preloaded_font(self.loaded_font_name)
        rows = np.matrix([
            [] for _ in range(0, self.font.get_char_height())
        ])
        print("Rendering text:", self.configuration["Text"].value)
        i = 0
        for char in self.configuration["Text"].value:
            rows = self.append_character(rows, self.font[char.lower()], spacing= 0 if i == 0 else self.configuration["Letter Spacing"].value)
            i += 1
        
        for y in range(0, len(rows)):
            for x in range(0, len(rows[y])):
                rows[y][x] *= self.configuration["Brightness"].value
        self.current_render = rows
        return rows

    def get_frame(self):
        return self.render()
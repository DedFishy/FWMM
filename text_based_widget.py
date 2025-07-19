from widget import Widget as WidgetBase
import numpy as np
from font_loader import load_preloaded_font, get_fonts


class TextBasedWidget(WidgetBase):
    name = "Text Based Widget"
    allow_rotation = True
    current_render: np.matrix = np.matrix([[]])
    rotation = 0
    font = None
    loaded_font_name = None

    def __init__(self):
        super().__init__()
        self.configuration = {}

    def get_text(self): return ""
    def get_font(self): return get_fonts()[0]
    def get_brightness(self): return 255
    def get_spacing(self): return 1

    def get_current_size(self):
        return [self.current_render.shape[1], self.current_render.shape[0]]
    
    def get_desired_spf(self):
        return -1
    
    def append_character(self, matrix: np.matrix, character: np.matrix, spacing=1):
        spacer = [
            [0 for _ in range(0, spacing)] for _ in range(0, matrix.shape[0])
        ]
        matrix = np.concatenate((matrix, np.matrix(spacer)), axis=1) # type: ignore
        matrix = np.concatenate((matrix, character), axis=1) # type: ignore
        return matrix
    
    def render(self,):
        if self.font == None or self.loaded_font_name != self.get_font():
            self.loaded_font_name = self.get_font()
            self.font = load_preloaded_font(self.loaded_font_name)
        rows = np.matrix([
            [] for _ in range(0, self.font.get_char_height())
        ])
        i = 0
        for char in self.get_text():
            rows = self.append_character(rows, self.font[char.lower()], spacing= 0 if i == 0 else self.get_spacing())
            i += 1
        
        for y in range(0, len(rows)):
            for x in range(0, len(rows[y])):
                rows[y][x] *= self.get_brightness()
        self.current_render = rows
        return rows

    def get_frame(self):
        return self.render()
import json
import os
import numpy as np
import util

class Font:
    font_dict = {}
    _first_character = ""
    def __init__(self, font_dict):
        self.font_dict = font_dict
        self._first_character = self.get_available_characters()[0]
    
    def get_available_characters(self):
        return list(self.font_dict.keys())
    
    def get_character(self, character) -> np.matrix:
        return np.matrix(self.font_dict[character])
    
    def get_char_width(self):
        return len(self.font_dict[self._first_character][0])
    
    def get_char_height(self):
        return len(self.font_dict[self._first_character])
     
    def __getitem__(self, key):
        return self.font_dict[str(key)]

def load_font(path):
    with open(path, "r") as font_file:
        content = json.loads(font_file.read())
    return Font(content)

def load_preloaded_font(font_name):
    return load_font(util.get_file_path(os.path.join("fonts", font_name))+ ".json")

def get_fonts():
    return [x.removesuffix(".json") for x in os.listdir(util.get_file_path("fonts"))]
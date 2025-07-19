import json
import os
import numpy as np
import util

class Font:
    """Represents a font loaded from a JSON file and made of pixels"""
    font_dict = {}
    _first_character = ""
    def __init__(self, font_dict):
        self.font_dict = font_dict
        self._first_character = self.get_available_characters()[0]
    
    def get_available_characters(self) -> list[str]:
        """Get a list of characters present in the font"""
        return list(self.font_dict.keys())
    
    def get_character(self, character) -> np.matrix:
        """Get a matrix representing a character in the font"""
        return np.matrix(self.font_dict[character])
    
    def get_char_width(self) -> int:
        """Get the width of each character"""
        return len(self.font_dict[self._first_character][0])
    
    def get_char_height(self) -> int:
        """Get the height of each character"""
        return len(self.font_dict[self._first_character])
     
    def __getitem__(self, key):
        """Get a character from the font"""
        return self.font_dict[str(key)]

def load_font(path) -> Font:
    """Creates a font object from a given font path"""
    with open(path, "r") as font_file:
        content = json.loads(font_file.read())
    return Font(content)

def load_preloaded_font(font_name) -> Font:
    """Creates a font object by loading it from the internal font folder"""
    return load_font(util.get_file_path(os.path.join("fonts", font_name))+ ".json")

def get_fonts() -> list[str]:
    """Get a list of fonts in the font folder"""
    return [x.removesuffix(".json") for x in os.listdir(util.get_file_path("fonts"))]
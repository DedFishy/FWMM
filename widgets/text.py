from datetime import datetime
import util
from text_based_widget import TextBasedWidget
from widget_config_item import WidgetConfigItem as Config
from widget_config_item import ConfigItemType as ConfigType
from const import WIDTH, HEIGHT
import numpy as np
from font_loader import load_preloaded_font, get_fonts


class Widget(TextBasedWidget):
    name = "Text"

    def __init__(self):
        super().__init__()
        self.configuration = {
            "Brightness": Config(ConfigType.integer, 255, 0, 255),
            "Font": Config(ConfigType.combo, get_fonts()[0], options=get_fonts()),
            "Text": Config(ConfigType.text, "Text"),
            "Letter Spacing": Config(ConfigType.integer, 1, 0, 10),

        }

    def get_brightness(self):
        return self.configuration["Brightness"].value
    def get_font(self):
        return self.configuration["Font"].value
    def get_spacing(self):
        return self.configuration["Letter Spacing"].value
    def get_text(self):
        return self.configuration["Text"].value
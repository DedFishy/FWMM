from widget import Widget

from widget_config_item import ConfigItemType
from const import MATRIX_SCALE

from random import randint


class WidgetObjectLayout:

    widget: Widget
    layout_manager = None
    color = None
    showing_config = False

    def __init__(self, widget: Widget, layout_manager, color = None):
        if not color: self.color = (randint(0, 255), randint(0, 255), randint(0, 255), 255)
        else: self.color = color
        self.widget = widget
        self.layout_manager = layout_manager
    
    def get_current_size(self):
        size = self.widget.get_current_size()
        if self.widget.rotation == 90 or self.widget.rotation == 270: size.reverse()
        return size
    
    def create_first_widget_bounds(self):
        return (self.widget.position[0] * MATRIX_SCALE, self.widget.position[1] * MATRIX_SCALE)

    def create_second_widget_bounds(self):
        return ((self.widget.position[0] + self.get_current_size()[0]) * MATRIX_SCALE, (self.widget.position[1] + self.get_current_size()[1]) * MATRIX_SCALE)
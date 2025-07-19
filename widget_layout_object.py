from widget import Widget
from random import randint

class WidgetObjectLayout:
    """Wraps a widget + layout information for use in the layout_manager"""

    widget: Widget
    layout_manager = None
    color = None
    showing_config = False

    def __init__(self, widget: Widget, layout_manager, color = None):
        if not color: self.color = (randint(0, 255), randint(0, 255), randint(0, 255), 255)
        else: self.color = color
        self.widget = widget
        self.layout_manager = layout_manager
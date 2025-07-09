from widget import Widget as WidgetBase
from widget_config_item import WidgetConfigItem as Config
from widget_config_item import ConfigItemType as ConfigType

class Widget(WidgetBase):
    name = "My Widget" # The name of the widget that will appear as its header in the layout
    desired_spf = -1 # The number of seconds between each rendered frame of your widget
    allow_rotation = False # Whether your widget can be rotated (0, 90, 180, or 270 degrees).

    def __init__(self):
        super().__init__()
        self.configuration = {
            "Number": Config(ConfigType.integer, 5, 0, 10) # One of the configuration options. Allows for numbers between 0 and 10, but default to 5.
        }

    def get_current_size(self): # Get the current size of your widget.
        return [3, 3]
    
    def get_desired_spf(self): # If your widget requires a dynamic refresh rate depending on your config, you can return that here.
        return -1

    def get_frame(self): # Return either a Numpy 2D matrix or a nested list matrix representing the brightness of each pixel contained in your widget (0 to 255)
        return [
            [255, 255, 255],
            [255, 255, 255],
            [255, 255, 255]
        ]
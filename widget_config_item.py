from enum import Enum

class ConfigItemType(Enum):
    text = 0
    integer = 1
    float = 2
    integer_list = 3
    float_list = 4
    boolean = 5
    combo = 6

class WidgetConfigItem:
    value = None

    config_item_type: ConfigItemType = -1

    minimum: int = 0
    maximum: int = 0
    options: list = []

    def __init__(self, type: ConfigItemType, value, minimum=0, maximum=0, options=[]):
        self.value = value
        self.minimum = minimum
        self.maximum = maximum
        self.config_item_type = type
        self.options = options
    
    def serialize(self):
        return {
            "value": self.value,
            "item_type": self.config_item_type.value,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "options": self.options
        }
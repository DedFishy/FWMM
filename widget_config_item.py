from enum import Enum

class ConfigItemType(Enum):
    text = 0
    integer = 1
    #float = 2
    #integer_list = 3
    #float_list = 4
    boolean = 5
    combo = 6

class WidgetConfigItem:
    value = None

    config_item_type: ConfigItemType = ConfigItemType.integer

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
    
    # For updating values based on what the frontend returns (which is encoded as a string by default)
    def update_value(self, new_value):
        if self.config_item_type == ConfigItemType.text: self.value = str(new_value)
        elif self.config_item_type == ConfigItemType.integer: self.value = int(new_value)
        #elif self.config_item_type == ConfigItemType.float: self.value = float(new_value)
        #elif self.config_item_type == ConfigItemType.integer_list: self.value = [int(x) for x in list(new_value)]
        #elif self.config_item_type == ConfigItemType.float_list: self.value = [float(x) for x in list(new_value)]
        elif self.config_item_type == ConfigItemType.boolean: self.value = bool(new_value)
        elif self.config_item_type == ConfigItemType.combo: self.value = str(new_value)
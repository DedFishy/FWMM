import os
import importlib
from pathlib import Path
import sys
import util
from widget import Widget
from widget_config_item import WidgetConfigItem


class WidgetManager:
    widgets: dict[str, Widget] = {}
    errors = {}
    def __init__(self):
        widget_files = os.listdir(util.get_file_path("widgets"))
        for widget_file in widget_files:
            if widget_file.endswith(".py"):
                name = widget_file.removesuffix(".py")
                try:
                    self.widgets[name] = importlib.import_module("widgets." + name).Widget
                    self.widgets[name].import_name = name
                except ImportError as e:
                    self.errors[name] = str(e)

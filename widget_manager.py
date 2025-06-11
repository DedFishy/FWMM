import os
import importlib
from pathlib import Path
import sys
import util
from widget import Widget


class WidgetManager:
    widgets: dict[str, Widget] = {}
    def __init__(self):
        widget_files = os.listdir(util.get_file_path("widgets"))
        for widget_file in widget_files:
            if widget_file.endswith(".py"):
                try:
                    name = widget_file.removesuffix(".py")
                    self.widgets[name] = importlib.import_module("widgets." + name).Widget
                except ImportError as e:
                    print("Failed to load widget: " + str(e))
import os
import importlib
import util
from widget import Widget


class WidgetManager:
    """Handles collecting all of the widget files and creating a structure for accessing them"""
    widgets: dict[str, Widget] = {}
    errors = {}
    def __init__(self):
        widget_files = os.listdir(util.get_file_path("widgets"))
        for widget_file in widget_files: # Iterate through widget files
            if widget_file.endswith(".py"):
                name = widget_file.removesuffix(".py")
                try:
                    self.widgets[name] = importlib.import_module("widgets." + name).Widget # Import the widget from its file
                    self.widgets[name].import_name = name # Apply the widget import name to the widget
                except ImportError as e:
                    self.errors[name] = str(e) # Add this widget to the error dictionary with the given error
        


import json
import os
from pathlib import Path
import threading
from typing import Callable

from config import Config
from const import HEIGHT, MATRIX_OFFSET, MATRIX_SCALE, WIDTH
from layout_manager import LayoutManager
from matrix import Matrix
from matrix_connector import MatrixConnector
from platform_specific import PlatformSpecificFunctions
import util
from widget import Widget
from widget_manager import WidgetManager

class Window:

    window_handle = None
    layout_manager = None
    widget_manager = None
    matrix_connector = None
    matrix_rep = None
    platform_specific = None
    config: Config

    send_to_tray = None
    kill_callback = None
    update_window_open = None

    def __init__(
            self, 
            layout_manager: LayoutManager, 
            widget_manager: WidgetManager, 
            matrix_connector: MatrixConnector, 
            matrix_rep: Matrix, 
            platform_specific_functions: PlatformSpecificFunctions,
            config: Config,
            send_to_tray_callback: Callable,
            kill_callback: Callable,
            update_window_open: Callable
        ):
        self.layout_manager = layout_manager
        self.widget_manager = widget_manager
        self.matrix_connector = matrix_connector
        self.matrix_rep = matrix_rep
        self.platform_specific = platform_specific_functions
        self.config = config
        self.send_to_tray = send_to_tray_callback
        self.kill_callback = kill_callback
        self.update_window_open = update_window_open

    def set_preview_pixel(self, x, y, value):
        #dpg.configure_item(f"{x}x{y}", fill=(255, 255, 255, value))
        pass

    def set_default_layout(self):
        #self.config.default_layout = self.layout_manager.selected_layout_file_path
        self.config.save_config()
        #print("Set default to:", self.layout_manager.selected_layout_file_path)

    def update_matrix_preview(self):
        for y in range(0, HEIGHT):
            for x in range(0, WIDTH):
                #self.set_preview_pixel(x, y, self.matrix_rep.get_led(x, y))
                pass
    
    def create_widget(self, widget, import_name, is_loaded=False, position=None, rotation=None, color=None, config=None, rerender=True):
        widget_instance: Widget = widget()
        widget_instance.import_name = import_name
        #if is_loaded:
            #widget_instance.position = position
            #widget_instance.rotation = rotation
            #for field in config.keys():
            #    widget_instance.configuration[field].value = config[field]
        #self.layout_manager.add_widget(widget_instance, color + [255] if color is not None else None)
        #if rerender:
            #self.layout_manager.render()
            #self.matrix_connector.flush_matrix()
            #self.update_matrix_preview()

    def load_widget_layout(self, _, app_data):
        #if app_data["file_path_name"]:
            #self.layout_manager.selected_layout_file_path = app_data["file_path_name"]
            #self.layout_manager.selected_layout_file_name = app_data["file_name"]
            #dpg.set_value("loaded_widget_layout", self.layout_manager.selected_layout_file_name)
            #with open(self.layout_manager.selected_layout_file_path) as file:
            #    layout = json.loads(file.read())
            #    self.layout_manager.remove_all()
            #    for widget in layout["widgets"]:
            #        self.create_widget(self.widget_manager.widgets[widget["import_name"]], widget["import_name"], True, widget["position"], widget["rotation"], widget["color"], widget["configuration"], rerender=False)
            #dpg.configure_item("widget_layout_file_namer", default_path=Path(self.layout_manager.selected_layout_file_path).parent, default_filename = self.layout_manager.selected_layout_file_name)
            #print(self.layout_manager.selected_layout_file_path)
        #self.resize_main_window()
        #self.layout_manager.render()
        #self.matrix_connector.flush_matrix()
        #self.update_matrix_preview()
        pass
    
    def save_widget_layout(self, _, app_data):
    
        #if app_data["file_path_name"]:
            #self.layout_manager.selected_layout_file_path = app_data["file_path_name"]
            #self.layout_manager.selected_layout_file_name = app_data["file_name"]
            #dpg.set_value("loaded_widget_layout", self.layout_manager.selected_layout_file_name)
            #with open(self.layout_manager.selected_layout_file_path, "w+") as file:
            #    file.write(json.dumps(self.layout_manager.generate_layout_dict()))
        pass
    


    def initialize_window(self):
        pass
    
    def resize_main_window(self, *_):
        #dpg.configure_item("Main Window", width=dpg.get_viewport_width(), height=dpg.get_viewport_width())
        pass
    
    def start(self):
        pass

    def start_as_thread(self):
        self.thread = threading.Thread(target=self.start)
        self.thread.start()

    def hide(self):
        pass
    
    def show(self):
        pass
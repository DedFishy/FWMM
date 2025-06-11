import json
import os
from pathlib import Path
import threading
from typing import Callable
import dearpygui.dearpygui as dpg
from pywinctl import getWindowsWithTitle

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
    config = None

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
        dpg.configure_item(f"{x}x{y}", fill=(255, 255, 255, value))

    def set_default_layout(self):
        self.config.default_layout = self.layout_manager.selected_layout_file_path
        self.config.save_config()
        print("Set default to:", self.layout_manager.selected_layout_file_path)

    def update_matrix_preview(self):
        for y in range(0, HEIGHT):
            for x in range(0, WIDTH):
                self.set_preview_pixel(x, y, self.matrix_rep.get_led(x, y))
    
    def create_widget(self, widget, import_name, is_loaded=False, position=None, rotation=None, color=None, config=None, rerender=True):
        widget_instance: Widget = widget()
        widget_instance.import_name = import_name
        if is_loaded:
            widget_instance.position = position
            widget_instance.rotation = rotation
            for field in config.keys():
                widget_instance.configuration[field].value = config[field]
        self.layout_manager.add_widget(widget_instance, color + [255] if color is not None else None)
        if rerender:
            self.layout_manager.render()
            self.matrix_connector.flush_matrix()
            self.update_matrix_preview()

    def load_widget_layout(self, _, app_data):
        if app_data["file_path_name"]:
            self.layout_manager.selected_layout_file_path = app_data["file_path_name"]
            self.layout_manager.selected_layout_file_name = app_data["file_name"]
            dpg.set_value("loaded_widget_layout", self.layout_manager.selected_layout_file_name)
            with open(self.layout_manager.selected_layout_file_path) as file:
                layout = json.loads(file.read())
                self.layout_manager.remove_all()
                for widget in layout["widgets"]:
                    self.create_widget(self.widget_manager.widgets[widget["import_name"]], widget["import_name"], True, widget["position"], widget["rotation"], widget["color"], widget["configuration"], rerender=False)
            dpg.configure_item("widget_layout_file_namer", default_path=Path(self.layout_manager.selected_layout_file_path).parent, default_filename = self.layout_manager.selected_layout_file_name)
            print(self.layout_manager.selected_layout_file_path)
        self.resize_main_window()
        self.layout_manager.render()
        self.matrix_connector.flush_matrix()
        self.update_matrix_preview()
    
    def save_widget_layout(self, _, app_data):
    
        if app_data["file_path_name"]:
            self.layout_manager.selected_layout_file_path = app_data["file_path_name"]
            self.layout_manager.selected_layout_file_name = app_data["file_name"]
            dpg.set_value("loaded_widget_layout", self.layout_manager.selected_layout_file_name)
            with open(self.layout_manager.selected_layout_file_path, "w+") as file:
                file.write(json.dumps(self.layout_manager.generate_layout_dict()))
    


    def initialize_window(self):
        dpg.create_context()

        with dpg.font_registry():
            default_font = dpg.add_font(util.get_file_path("font.ttf"), 20)

        print("setup")

        dpg.create_viewport(title="Framework Matrix Manager", width=1000, height=600, small_icon=util.get_file_path("icon.ico"),large_icon=util.get_file_path("icon.ico"), disable_close=True)
        dpg.set_exit_callback(self.kill_callback)
        print("setup_dearpygui")
        dpg.setup_dearpygui()
        print("creating everything")

        with dpg.file_dialog(
            directory_selector=False, modal=True, show=False, callback=self.load_widget_layout, tag="widget_layout_file_selector", width=700 ,height=400):
            dpg.add_file_extension("FWMM Widget Layout (.mmw){.mmw}")

        with dpg.file_dialog(
            directory_selector=False, modal=True, show=False, callback=self.save_widget_layout, tag="widget_layout_file_namer", width=700 ,height=400):
            dpg.add_file_extension("FWMM Widget Layout (.mmw){.mmw}")

        with dpg.window(label = "Main Window", tag="Main Window", no_close=True, no_resize=True, no_title_bar=True, no_move=True, horizontal_scrollbar=True, no_background=True):
            with dpg.group(horizontal=True):
                with dpg.group(width=150):

                    # Control
                    dpg.add_text("FWMM")
                    dpg.add_button(label="Send to Tray", callback=lambda: self.send_to_tray())
                    dpg.add_button(label="Add to Startup", callback=lambda: self.platform_specific.add_self_to_startup())

                    # Widget Layout
                    with dpg.group(horizontal=True):
                        dpg.add_text("Layout:")
                        dpg.add_text("None selected", tag="loaded_widget_layout")
                    dpg.add_button(label="Load Layout", callback=lambda: dpg.show_item("widget_layout_file_selector"))
                    dpg.add_button(label="Save Layout", callback=lambda: dpg.show_item("widget_layout_file_namer"))
                    dpg.add_button(label="Set As Default", callback=lambda: self.set_default_layout())

                    dpg.bind_font(default_font)

                with dpg.group():
                    dpg.add_text("Preview")
                    with dpg.drawlist(width = WIDTH * MATRIX_SCALE, height = HEIGHT * MATRIX_SCALE):
                        for x in range(0, WIDTH):
                            for y in range(0, HEIGHT):
                                dpg.draw_circle((x*MATRIX_SCALE+MATRIX_OFFSET, y*MATRIX_SCALE+MATRIX_OFFSET), MATRIX_OFFSET, tag=f"{x}x{y}", color=(0, 0, 0, 0), fill=(255, 255, 255, 0))

                with dpg.group():
                    dpg.add_text("Layout")
                    with dpg.group(horizontal=True):
                        dpg.add_drawlist(width = WIDTH * MATRIX_SCALE, height = HEIGHT * MATRIX_SCALE, tag="widget-layout-parent")
                        dpg.add_group(horizontal=False, tag="widget-configurations", width=200)

                with dpg.group():
                    dpg.add_text("Add Widget")
                    for widget in self.widget_manager.widgets.keys():
                        widget_name = self.widget_manager.widgets[widget].name
                        dpg.add_button(label=widget_name, tag="create-" + widget, callback=lambda sender, _: self.create_widget(self.widget_manager.widgets[sender.removeprefix("create-")], sender.removeprefix("create-")))
        
        with dpg.theme() as global_theme:

            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
        

        dpg.bind_theme(global_theme)

        dpg.set_viewport_resize_callback(self.resize_main_window)
    
    def resize_main_window(self, *_):
        dpg.configure_item("Main Window", width=dpg.get_viewport_width(), height=dpg.get_viewport_width())
    
    def start(self):
        self.update_window_open(True)
        dpg.show_viewport()
        handles = getWindowsWithTitle(dpg.get_viewport_title())
        print("Handles", handles)
        self.window_handle = handles[0]
        dpg.start_dearpygui()
        dpg.destroy_context()

    def start_as_thread(self):
        self.thread = threading.Thread(target=self.start)
        self.thread.start()

    def hide(self):
        self.update_window_open(False)
        self.window_handle.hide(True)
    
    def show(self):
        self.update_window_open(True)
        self.window_handle.show(True)
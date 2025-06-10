import json
import os
from pathlib import Path
import time
from PIL import Image
import dearpygui.dearpygui as dpg
import pystray
from config import Config
import util
import detect
from const import WIDTH, HEIGHT, MATRIX_SCALE, MATRIX_OFFSET
from matrix import Matrix
from matrix_connector import MatrixConnector
from widget import Widget
from widget_manager import WidgetManager
from layout_manager import LayoutManager
from widget_layout_object import WidgetObjectLayout
import sys
import platform_specific
import random

config = Config()

matrix_rep = Matrix()
matrix_connector = MatrixConnector(matrix_rep)

widget_manager = WidgetManager()

platform_specific_functions = platform_specific.get_class()

running = True
waiting_for_tray = False

def flush_layout_manager():
    matrix_connector.flush_matrix()
    update_matrix_preview()
layout_manager = LayoutManager(matrix_rep, lambda: flush_layout_manager())

icon_image = Image.open("icon.png")

def kill():
        global running, waiting_for_tray
        waiting_for_tray = False
        dpg.destroy_context()
        icon.stop()
        running = False

def reveal_from_tray():
    global waiting_for_tray
    waiting_for_tray = False

icon = pystray.Icon("FWMM", icon_image, "Framework Matrix Manager", menu=pystray.Menu(
        pystray.MenuItem("Open Window", lambda: reveal_from_tray()),
        pystray.MenuItem("Exit", lambda: kill())
    ))

icon.run_detached(lambda: None)

selected_layout_file_path = None
selected_layout_file_name = None

ports = {}

def try_connect_matrix():
    print("connecting to matrix")
    port = dpg.get_value("com_port_select")
    try:
        print("going for it")
        matrix_connector.connect(port)
    except Exception as e:
        print(e)

def get_active_ports():
    print("getting active ports")
    ports = detect.get_active_ports()
    
    dpg.configure_item("com_port_select", items=list(ports.keys()))

    for port in ports.keys():
        if util.eval_is_matrix(ports[port][1]):
            dpg.set_value("com_port_select", port)
            try_connect_matrix()



def set_matrix_pixel(x, y, value):
    matrix_rep.set_led(x, y, value)
    matrix_connector.flush_matrix()
    set_preview_pixel(x, y, value)

def set_preview_pixel(x, y, value):
    dpg.configure_item(f"{x}x{y}", fill=(255, 255, 255, value))

def load_widget_layout(_, app_data):
    global selected_layout_file_path, selected_layout_file_name
    selected_layout_file_path = app_data["file_path_name"]
    selected_layout_file_name = app_data["file_name"]
    print(selected_layout_file_path)
    if selected_layout_file_path:
        dpg.set_value("loaded_widget_layout", selected_layout_file_name)
        with open(selected_layout_file_path) as file:
            layout = json.loads(file.read())
            layout_manager.remove_all()
            for widget in layout["widgets"]:
                create_widget(widget_manager.widgets[widget["import_name"]], widget["import_name"], True, widget["position"], widget["rotation"], widget["color"], widget["configuration"])
        dpg.configure_item("widget_layout_file_namer", default_path=Path(selected_layout_file_path).parent, default_filename = selected_layout_file_name)
        print(selected_layout_file_path)

def load_config():
    if config.default_layout:
        load_widget_layout(None, {
            "file_path_name": config.default_layout,
            "file_name": Path(config.default_layout).name
        })

def generate_layout_dict():
    return {
        "widgets": [
            {
                "position": widget.widget.position,
                "rotation": widget.widget.rotation,
                "color": widget.color,
                "import_name": widget.widget.import_name,
                "configuration": {field: widget.widget.configuration[field].value for field in widget.widget.configuration.keys()}
            } for widget in layout_manager.widgets
        ]
    }

def save_widget_layout(_, app_data):
    global selected_layout_file_path, selected_layout_file_name
    selected_layout_file_path = app_data["file_path_name"]
    selected_layout_file_name = app_data["file_name"]
    if selected_layout_file_path:
        dpg.set_value("loaded_widget_layout", selected_layout_file_name)
        with open(selected_layout_file_path, "w+") as file:
            file.write(json.dumps(generate_layout_dict()))

def update_matrix_preview():
    for y in range(0, HEIGHT):
        for x in range(0, WIDTH):
            set_preview_pixel(x, y, matrix_rep.get_led(x, y))
            

def create_widget(widget, import_name, is_loaded=False, position=None, rotation=None, color=None, config=None):
    widget_instance: Widget = widget()
    widget_instance.import_name = import_name
    if is_loaded:
        widget_instance.position = position
        widget_instance.rotation = rotation
        for field in config.keys():
            widget_instance.configuration[field].value = config[field]
    layout_manager.add_widget(widget_instance, color + [255] if color is not None else None)
    layout_manager.render()
    matrix_connector.flush_matrix()
    update_matrix_preview()


def set_default_layout(*_):
    config.default_layout = selected_layout_file_path
    config.save_config()
    print("Set default to:", selected_layout_file_path)

def launch_window(skip_window = False):
    global waiting_for_tray

    print("creating context")

    icon.visible = False
    dpg.create_context()

    with dpg.font_registry():
        default_font = dpg.add_font("assets/font.ttf", 20)

    print("setup")

    dpg.create_viewport(title="Framework Matrix Manager", width=1000, height=600, small_icon="icon.ico",large_icon="icon.ico")
    print("setup_dearpygui")
    if not skip_window: dpg.setup_dearpygui()
    print("creating everything")

    with dpg.file_dialog(
        directory_selector=False, modal=True, show=False, callback=load_widget_layout, tag="widget_layout_file_selector", width=700 ,height=400):
        dpg.add_file_extension("FWMM Widget Layout (.mmw){.mmw}")

    with dpg.file_dialog(
        directory_selector=False, modal=True, show=False, callback=save_widget_layout, tag="widget_layout_file_namer", width=700 ,height=400):
        dpg.add_file_extension("FWMM Widget Layout (.mmw){.mmw}")

    with dpg.window(label = "Main Window", tag="Main Window", no_close=True, no_resize=True, no_title_bar=True, no_move=True, horizontal_scrollbar=True, no_background=True):
        with dpg.group(horizontal=True):
            with dpg.group(width=150):

                # Control
                dpg.add_text("FWMM")
                dpg.add_button(label="Exit", callback=lambda: kill())
                dpg.add_button(label="Add to Startup", callback=lambda: platform_specific_functions.add_self_to_startup())

                # COM Port
                dpg.add_text("Connection")
                dpg.add_combo([], label="", tag="com_port_select", callback=try_connect_matrix)
                dpg.add_button(label="Rescan", callback=get_active_ports)

                # Widget Layout
                with dpg.group(horizontal=True):
                    dpg.add_text("Layout:")
                    dpg.add_text("None selected", tag="loaded_widget_layout")
                dpg.add_button(label="Load Layout", callback=lambda: dpg.show_item("widget_layout_file_selector"))
                dpg.add_button(label="Save Layout", callback=lambda: dpg.show_item("widget_layout_file_namer"))
                dpg.add_button(label="Set As Default", callback=set_default_layout)

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
                for widget in widget_manager.widgets.keys():
                    widget_name = widget_manager.widgets[widget].name
                    dpg.add_button(label=widget_name, tag="create-" + widget, callback=lambda sender, _: create_widget(widget_manager.widgets[sender.removeprefix("create-")], sender.removeprefix("create-")))
    
    with dpg.theme() as global_theme:

        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)

    dpg.bind_theme(global_theme)
    print("ports")

    get_active_ports()
    print("config")
    load_config()

    def resize_main_window(*_):
        dpg.configure_item("Main Window", width=dpg.get_viewport_width(), height=dpg.get_viewport_width())

    dpg.set_viewport_resize_callback(resize_main_window)
    

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

    matrix_connector.get_sleep() # To wake it up so it doesn't conk out on the first frame

    spf = layout_manager.get_desired_spf()
    print("Starting rendering loop at SPF=", spf)
    icon.visible = True
    waiting_for_tray = True
    seconds_to_next_frame = spf
    while waiting_for_tray:
        print("Sitting around")
        time.sleep(1)
        seconds_to_next_frame -= 1
        if (seconds_to_next_frame <= 0):
            print("Rendering next frame")
            layout_manager.render()
            matrix_connector.flush_matrix()
            seconds_to_next_frame = spf
    
if __name__ == "__main__":
    skip_window = "skip-window" in sys.argv
    while running:
        print("do it:", skip_window)
        launch_window(skip_window)
        skip_window = False
        print("finished loop")
    
    print("Done?")
    
    matrix_connector.set_sleep(True)
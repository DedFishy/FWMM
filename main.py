import json
import dearpygui.dearpygui as dpg
import util
import detect
from const import WIDTH, HEIGHT, MATRIX_SCALE, MATRIX_OFFSET
from matrix import Matrix
from matrix_connector import MatrixConnector
from widget import Widget
from widget_manager import WidgetManager
from layout_manager import LayoutManager
from widget_layout_object import WidgetObjectLayout

import random



matrix_rep = Matrix()
matrix_connector = MatrixConnector(matrix_rep)

widget_manager = WidgetManager()

def flush_layout_manager():
    matrix_connector.flush_matrix()
    update_matrix_preview()
layout_manager = LayoutManager(matrix_rep, lambda: flush_layout_manager())

def save_callback():
    print("Save Clicked")

dpg.create_context()

with dpg.font_registry():
    default_font = dpg.add_font("assets/font.ttf", 20)

dpg.create_viewport(title="Framework Matrix Manager")
dpg.setup_dearpygui()

selected_widget_file_path = None
selected_widget_file_name = None

ports = {}

def try_connect_matrix():
    port = dpg.get_value("com_port_select")
    try:
        matrix_connector.connect(port)
    except Exception as e:
        print(e)

def get_active_ports():
    ports = detect.get_active_ports()
    
    dpg.configure_item("com_port_select", items=list(ports.keys()))

    for port in ports.keys():
        if util.eval_is_matrix(ports[port][1]):
            dpg.set_value("com_port_select", port)
            try_connect_matrix()

def set_matrix_pixel(x, y, value):
    print(f"{x}x{y}")
    matrix_rep.set_led(x, y, value)
    matrix_connector.flush_matrix()
    set_preview_pixel(x, y, value)

def set_preview_pixel(x, y, value):
    dpg.configure_item(f"{x}x{y}", fill=(255, 255, 255, value))

def load_widget_layout(sender, app_data):
    selected_widget_file_path = app_data["file_path_name"]
    selected_widget_file_name = app_data["file_name"]
    if selected_widget_file_path:
        dpg.set_value("loaded_widget_layout", selected_widget_file_name)
        with open(selected_widget_file_path) as file:
            layout = json.loads(file.read())
            layout_manager.remove_all()
            for widget in layout["widgets"]:
                create_widget(widget_manager.widgets[widget["import_name"]], True, widget["position"], widget["rotation"], widget["color"], widget["configuration"])

def update_matrix_preview():
    for y in range(0, HEIGHT):
        for x in range(0, WIDTH):
            set_preview_pixel(x, y, matrix_rep.get_led(x, y))
            

def create_widget(widget, is_loaded=False, position=None, rotation=None, color=None, config=None):
    print(widget)
    widget_instance: Widget = widget()
    if is_loaded:
        widget_instance.position = position
        widget_instance.rotation = rotation
        for field in config.keys():
            widget_instance.configuration[field].value = config[field]
    layout_manager.add_widget(widget_instance, color + [255] if color is not None else None)
    layout_manager.render()
    matrix_connector.flush_matrix()
    update_matrix_preview()

with dpg.file_dialog(
    directory_selector=False, modal=True, show=False, callback=load_widget_layout, tag="widget_layout_file_selector", width=700 ,height=400):
    dpg.add_file_extension("FWMM Widget Layout (.mmw){.mmw}")

with dpg.window(label="Settings", tag="settings", no_close=True, autosize=True):
    # COM Port
    with dpg.group(horizontal=True):
        dpg.add_combo([], label="COM Port", tag="com_port_select", callback=try_connect_matrix)
        dpg.add_button(label="Rescan", callback=get_active_ports)
    # Widget Layout
    with dpg.group(horizontal=True):
        dpg.add_text("None selected", tag="loaded_widget_layout")
        dpg.add_button(label="Load Widget Layout", callback=lambda: dpg.show_item("widget_layout_file_selector"))

    dpg.bind_font(default_font)

with dpg.window(label="Matrix", tag="matrix", no_close=True, autosize=True):
    with dpg.drawlist(width = WIDTH * MATRIX_SCALE, height = HEIGHT * MATRIX_SCALE):
        for x in range(0, WIDTH):
            for y in range(0, HEIGHT):
                dpg.draw_circle((x*MATRIX_SCALE+MATRIX_OFFSET, y*MATRIX_SCALE+MATRIX_OFFSET), MATRIX_OFFSET, tag=f"{x}x{y}", color=(0, 0, 0, 0), fill=(255, 255, 255, 0))
    dpg.add_button(label="Experiment", callback=lambda: set_matrix_pixel(random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1), random.randint(0, 255)))

with dpg.window(label="Widget Layout", tag="widget-layout", no_close=True, autosize=True):
    with dpg.group(horizontal=True):
        dpg.add_drawlist(width = WIDTH * MATRIX_SCALE, height = HEIGHT * MATRIX_SCALE, tag="widget-layout-parent")
        dpg.add_group(horizontal=False, tag="widget-configurations")

with dpg.window(label="Widgets", tag="widgets", no_close=True, autosize=True):
    for widget in widget_manager.widgets.keys():
        widget_name = widget_manager.widgets[widget].name
        dpg.add_button(label=widget_name, callback=lambda: create_widget(widget_manager.widgets[widget]))
            

get_active_ports()

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
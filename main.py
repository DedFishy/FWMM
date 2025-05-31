import dearpygui.dearpygui as dpg
import util
import detect

def save_callback():
    print("Save Clicked")

dpg.create_context()

# add a font registry
with dpg.font_registry():
    # first argument ids the path to the .ttf or .otf file
    default_font = dpg.add_font("assets/font.ttf", 20)

dpg.create_viewport(title="Framework Matrix Manager")
dpg.setup_dearpygui()

ports = {}
def get_active_ports():
    ports = detect.get_active_ports()
    
    dpg.configure_item("com_port_select", items=list(ports.keys()))

    for port in ports.keys():
        if util.eval_is_matrix(ports[port][1]):
            dpg.set_value("com_port_select", port)

with dpg.window(label="Settings", tag="settings", no_close=True, autosize=True):
    dpg.add_text("Settings")
    dpg.add_combo([], label="COM Port", tag="com_port_select")
    dpg.add_same_line()
    dpg.add_button(label="Rescan", callback=get_active_ports)
    dpg.add_input_text(label="string")
    dpg.add_slider_float(label="float")

    dpg.bind_font(default_font)

with dpg.window(label="Matrix", tag="matrix", no_close=True, autosize=True):
    

get_active_ports()

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
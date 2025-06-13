from pathlib import Path
import time
from PIL import Image
import dearpygui.dearpygui as dpg
from plyer import notification
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
from window import Window
import font_loader # Recognized by freezer

running = True
is_window_open = False

config = Config()

matrix_rep = Matrix()
matrix_connector = MatrixConnector(matrix_rep)

widget_manager = WidgetManager()

platform_specific_functions = platform_specific.get_class()


def flush_layout_manager():
    matrix_connector.flush_matrix()
    window.update_matrix_preview()
layout_manager = LayoutManager(matrix_rep, lambda: flush_layout_manager())


icon_image = Image.open(util.get_file_path("icon.png"))

def send_to_tray(*_):
    window.hide()
    icon.visible = True

def kill():
        dpg.stop_dearpygui()
        dpg.destroy_context()
        icon.stop()

def reveal_from_tray():
    icon.visible = False
    window.show()

def update_is_window_open(is_open):
    global is_window_open
    is_window_open = is_open

window = Window(layout_manager, widget_manager, matrix_connector, matrix_rep, platform_specific_functions, config, send_to_tray, kill, update_is_window_open)

icon = pystray.Icon("FWMM", icon_image, "Framework Matrix Manager", menu=pystray.Menu(
        pystray.MenuItem("Open Window", reveal_from_tray, default=True),
        pystray.MenuItem("Exit", kill)
    ))

icon.run_detached(lambda *_: None)

ports = {}

def try_connect_matrix(port):
    print("connecting to matrix")
    try:
        print("going for it")
        matrix_connector.connect(port)
    except Exception as e:
        return e

def get_active_ports():
    print("getting active ports")
    ports = detect.get_active_ports()

    result = "No error recorded"

    for port in ports.keys():
        if util.eval_is_matrix(ports[port][1]):
            result = try_connect_matrix(port)
    
    return result



def set_matrix_pixel(x, y, value):
    matrix_rep.set_led(x, y, value)
    matrix_connector.flush_matrix()
    window.set_preview_pixel(x, y, value)





def load_config():
    if config.default_layout:
        window.load_widget_layout(None, {
            "file_path_name": config.default_layout,
            "file_name": Path(config.default_layout).name
        })




def matrix_update_loop():
    spf = layout_manager.get_desired_spf()
    print("Starting rendering loop at SPF=", spf)
    while running:
        if spf == -1: continue
        while is_window_open: 
            time.sleep(0.1) # Stop this loop until the window is hidden
            start_time = time.time()
            spf = layout_manager.get_desired_spf()
        print("Sitting around")
        
        time.sleep(0.25)
        seconds_elapsed = time.time() - start_time
        if (seconds_elapsed >= spf):
            start_time = time.time()
            print("Rendering next frame")
            try:
                layout_manager.render()
                matrix_connector.flush_matrix()
                spf = layout_manager.get_desired_spf()
            except Exception as e:
                print("Failed to write to serial:", e)

def main():
    skip_window = "skip-window" in sys.argv

    print("skip window? :", skip_window)

    window.initialize_window()

    time.sleep(5)

    error = get_active_ports()

    if not matrix_connector.is_connected():
        print("Couldn't connect to LED matrix:", error)
        notification.notify(
            title="Couldn't connect to LED matrix",
            message=str(error),
            app_icon=util.get_file_path("icon.ico")
        )
        dpg.stop_dearpygui()
        dpg.destroy_context()
        raise SystemExit
    
    print("config")
    load_config()

    window.start_as_thread()

    if skip_window:
        while not window.window_handle: time.sleep(0.01) # Wait for thread to initialize the window
        window.hide()
        icon.visible = True
    
    matrix_update_loop()

    print("finished loop")
    
    print("Done?")
    
    matrix_connector.set_sleep(True)
    

DEBUG = True
if __name__ == "__main__":
    if DEBUG: main()
    else:
        try:
            main()
        except Exception as e:
            notification.notify(
                title="FWMM has encountered an error",
                message=str(e)
            )
            dpg.stop_dearpygui()
            dpg.destroy_context()
            icon.stop()
            window.thread.join(0)

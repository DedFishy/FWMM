from pathlib import Path
import time
from PIL import Image
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
from flask import Flask, render_template, send_file, send_from_directory
from flask_socketio import SocketIO
import webbrowser
import os
import font_loader # Recognized by freezer

DEBUG = True

running = True

num_sockets_connected = 0

config = Config()

matrix_rep = Matrix()
matrix_connector = MatrixConnector(matrix_rep)

widget_manager = WidgetManager()

platform_specific_functions = platform_specific.get_class()

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = DEBUG
#app.config["DEBUG"] = DEBUG
app.config['SECRET_KEY'] = '48cyn04 qxfh9u8q9x8h9em9h9xn489nnrmfa'
socket = SocketIO(app)

@socket.on("connect")
def connect():
    global num_sockets_connected
    num_sockets_connected += 1

@socket.on("disconnect")
def disconnect():
    global num_sockets_connected
    num_sockets_connected -= 1

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/favicon.ico")
def favicon():
    return send_file("icon.ico")

def flush_layout_manager():
    matrix_connector.flush_matrix()
    #window.update_matrix_preview()

layout_manager = LayoutManager(matrix_rep, lambda: flush_layout_manager())

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
    #window.set_preview_pixel(x, y, value)

def load_config():
    pass
    #if config.default_layout:
    #    window.load_widget_layout(None, {
    #        "file_path_name": config.default_layout,
    #        "file_name": Path(config.default_layout).name
    #    })

def matrix_update_loop():
    spf = layout_manager.get_desired_spf()
    print("Starting rendering loop at SPF=", spf)
    while running:
        if spf == -1:
            continue
        while num_sockets_connected > 0: 
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


    print(os.system("whoami"))

    error = get_active_ports()

    if not matrix_connector.is_connected():
        print("Couldn't connect to LED matrix:", error)
        raise SystemExit
    
    
    print("config")
    load_config()

    #update_thread = socket.start_background_task(matrix_update_loop)

    print("Starting web server")

    if not skip_window and not DEBUG:
        print("Opening web page")
        webbrowser.open("http://127.0.0.1:5621")

    socket.run(app, "127.0.0.1", 5621)

    print("finished loop")
    
    print("Done?")
    
    matrix_connector.set_sleep(True)
    

if __name__ == "__main__":
    if DEBUG: main()
    else:
        try:
            main()
        except Exception as e:
            pass

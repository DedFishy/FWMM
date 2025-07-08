import asyncio
import json
from pathlib import Path
import random
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
from aiohttp import web
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

app = web.Application()
routes = web.RouteTableDef()

def construct_json_response(dictionary):
    return web.Response(text=json.dumps(dictionary), content_type="text/json")

def construct_full_update():
    dictionary = {
        "widgets": 
            [{
                "name": widget.widget.name,
                "config": {item: widget.widget.configuration[item].serialize() for item in widget.widget.configuration.keys()},
                "transform": {
                    "X": widget.widget.position[0],
                    "Y": widget.widget.position[1],
                    "Rotation": widget.widget.rotation
                },
                "size": widget.widget.get_current_size(),
                "color": widget.color,
                "index": layout_manager.widgets.index(widget)
                } for widget in layout_manager.widgets],
        "available": list(widget_manager.widgets.keys())
    }
    return construct_json_response(dictionary)

@routes.get("/")
async def index_handler(request):
    with open("index.html", "r+") as index_file:
        return web.Response(text=index_file.read(), content_type="text/html")
    
@routes.get("/fwmm.js")
async def js_handler(request):
    with open("static/fwmm.js", "r+") as fwmm_js:
        return web.Response(text=fwmm_js.read(), content_type="text/javascript")

@routes.get("/style.css")
async def css_handler(request):
    with open("static/style.css", "r+") as css:
        return web.Response(text=css.read(), content_type="text/css")
    
# API Definitiions
@routes.get("/initial")
async def available_widgets(request):
    return construct_full_update()

@routes.get("/createwidget/{widget}")
async def widget_meta(request):
    widget_name = request.match_info.get("widget", None)
    widget = widget_manager.widgets[widget_name]() # type: ignore
    widget.color = (random.randint(0, 255) for _ in range(3))

    layout_manager.add_widget(widget)

    print({item: widget.configuration[item].serialize() for item in widget.configuration.keys()})

    return construct_full_update()

@routes.get("/updatewidgetconfig/{widget_index}/{name}/{new_value}")
async def update_widget_config(request):
    widget_index = request.match_info.get("widget_index", None)
    print(widget_index)
    name = request.match_info.get("name", None)
    new_value = request.match_info.get("new_value", None)
    layout_manager.widgets[int(widget_index)].widget.configuration[name].update_value(new_value)

    return construct_full_update()

@routes.get("/updatewidgetcolor/{widget_index}/{new_value}")
async def update_widget_color(request):
    widget_index = request.match_info.get("widget_index", None)
    print(widget_index)
    new_value = request.match_info.get("new_value", None)
    layout_manager.widgets[int(widget_index)].color = tuple(int(new_value.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

    return construct_json_response({})

@routes.get("/updatewidgettransform/{widget_index}/{name}/{new_value}")
async def update_widget_transform(request):
    widget_index = request.match_info.get("widget_index", None)
    print(widget_index)
    name = request.match_info.get("name", None)
    new_value = request.match_info.get("new_value", None)
    target = layout_manager.widgets[int(widget_index)].widget
    if name == "X": target.position[0] = int(new_value)
    elif name == "Y": target.position[1] = int(new_value)
    elif name == "Rotation": target.rotation = int(new_value)
    else: print("Invalid transform variable", name)

    return construct_full_update()

@routes.get("/updatenow")
async def update_now(request):
    layout_manager.render()
    matrix_connector.flush_matrix()
    return construct_json_response({})

routes.static('/static', "static")

    
app.add_routes(routes)

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

async def background_tasks(app):
    global running
    app["matrix_update_loop"] = asyncio.create_task(
        matrix_update_loop()
    )
    yield
    running = False

    app["matrix_update_loop"].cancel()
    await app["matrix_update_loop"]

async def matrix_update_loop():
    spf = layout_manager.get_desired_spf()
    print("Starting rendering loop at SPF=", spf)
    start_time = time.time()
    while running:
        await asyncio.sleep(0.1)
        spf = layout_manager.get_desired_spf()

        if spf == -1: 
            await asyncio.sleep(1)
            continue
        
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
    global running
    skip_window = "skip-window" in sys.argv
    print("skip window? :", skip_window)


    print(os.system("whoami"))

    error = get_active_ports()

    if not matrix_connector.is_connected():
        print("Couldn't connect to LED matrix:", error)
        raise SystemExit
    
    
    print("config")
    load_config()

    app.cleanup_ctx.append(background_tasks)

    print("Starting web server")

    if not skip_window and not DEBUG:
        print("Opening web page")
        webbrowser.open("http://127.0.0.1:5621")

    app.cleanup_ctx.append(background_tasks)

    web.run_app(app, host="127.0.0.1", port=5621)
    running = False


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

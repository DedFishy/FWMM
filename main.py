import asyncio
import json
import random
import time
from config import Config
import util
import detect
from matrix import Matrix
from matrix_connector import MatrixConnector
from widget import Widget
from widget_manager import WidgetManager
from layout_manager import LayoutManager
import sys
import platform_specific
from aiohttp import web
import webbrowser
import os
import filedialpy
import font_loader # Recognized by freezer
import signal


def shutdown():
    signal.raise_signal(signal.SIGTERM)

DEBUG = True

running = True

error = ""

num_sockets_connected = 0


config = Config()

matrix_rep = Matrix()
matrix_connector = MatrixConnector(matrix_rep)

widget_manager = WidgetManager()

platform_specific_functions = platform_specific.get_class()

queued_notifications = []

if len(widget_manager.errors.keys()) > 0:
    queued_notifications.append("Failed to load widgets:\n" + "\n".join([error + ": " + widget_manager.errors[error] for error in widget_manager.errors.keys()]))

app = web.Application()
routes = web.RouteTableDef()

def get_local_path(path):
    if platform_specific_functions.is_frozen:
        return "_internal/" + path
    return path

def construct_json_response(dictionary):
    return web.Response(text=json.dumps(dictionary), content_type="text/json")

def construct_full_update():
    global queued_notifications
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
                "index": layout_manager.widgets.index(widget),
                "can_rotate": widget.widget.allow_rotation,
                } for widget in layout_manager.widgets],
        "available": {widget.name: widget.import_name for widget in widget_manager.widgets.values()},
        "notifications": queued_notifications.copy()
    }
    queued_notifications = []
    return construct_json_response(dictionary)

if not DEBUG:
    with open(get_local_path("index.html"), "r+") as index_file:
        html = index_file.read()
    with open(get_local_path("static/fwmm.js"), "r+") as fwmm_js:
        js = fwmm_js.read()
    with open(get_local_path("static/style.css"), "r+") as css_file:
        css = css_file.read()
    with open(get_local_path("font_maker/index.html"), "r+") as font_maker_file:
        font_maker = font_maker_file.read()

@routes.get("/font_maker")
async def font_maker(request):
    if DEBUG:
        with open(get_local_path("font_maker/index.html"), "r+") as font_maker_file:
            return web.Response(text=font_maker_file.read(), content_type="text/html")
    return web.Response(text=font_maker, content_type="text/html")

@routes.get("/")
async def index_handler(request):
    global error
    if not running:
        error = str(error)
        if "[Errno 13]" in error:
            error = "Permission to access your matrix was denied. Please run 'sudo chmod 666 " + error.split(" ")[-1].replace("'", "") + "' to allow FWMM to connect to your input module."
        return web.Response(body=f"""
<!DOCTYPE html>
<html>
    <head>
        <title>Error!</title>
        <link rel="stylesheet" href="/style.css">
        <link rel="icon" type="image/x-icon" href="/static/icon.ico">
    </head>
    <body id='error'>
        <h1>Couldn't connect to LED matrix</h1>
        <h2>{str(error)}</h2>
        <button onclick='fetch("/stop"); document.body.innerHTML = "<h1>FWMM has shut down.</h1>"'>Got it</button>
    </body>
</html>""", content_type="text/html")
    if DEBUG:
        with open(get_local_path("index.html"), "r+") as index_file:
            return web.Response(text=index_file.read(), content_type="text/html")
    return web.Response(text=html, content_type="text/html")
    
@routes.get("/fwmm.js")
async def js_handler(request):
    if DEBUG:
        with open(get_local_path("static/fwmm.js"), "r+") as fwmm_js:
            return web.Response(text=fwmm_js.read(), content_type="text/javascript")
    return web.Response(text=js, content_type="text/javascript")

@routes.get("/style.css")
async def css_handler(request):
    global css
    if DEBUG:
        with open(get_local_path("static/style.css"), "r+") as css:
            return web.Response(text=css.read(), content_type="text/css")
    return web.Response(text=css, content_type="text/css")
    
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

    layout_manager.render()
    matrix_connector.flush_matrix()

    return construct_full_update()

@routes.get("/updatewidgetconfig/{widget_index}/{name}/{new_value}")
async def update_widget_config(request):
    widget_index = request.match_info.get("widget_index", None)
    print(widget_index)
    name = request.match_info.get("name", None)
    new_value = request.match_info.get("new_value", None)
    layout_manager.widgets[int(widget_index)].widget.configuration[name].update_value(new_value)

    layout_manager.render()
    matrix_connector.flush_matrix()

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

    layout_manager.render()
    matrix_connector.flush_matrix()

    return construct_full_update()

@routes.get("/deletewidget/{widget_index}")
async def delete_widget(request):
    widget_index = request.match_info.get("widget_index", None)
    layout_manager.remove(layout_manager.widgets[int(widget_index)])
    layout_manager.render()
    matrix_connector.flush_matrix()
    return construct_full_update()

@routes.get("/updatenow")
async def update_now(request):
    layout_manager.render()
    matrix_connector.flush_matrix()
    return construct_full_update()

@routes.get("/savelayout")
async def save_layout(request):
    file = filedialpy.saveFile(filter="*.mmw", title="Save layout")
    if file:
        layout_manager.selected_layout_file_path = file
        layout_manager.selected_layout_file_name = file.split("/")[-1]
        with open(layout_manager.selected_layout_file_path, "w+") as file:
            file.write(json.dumps(layout_manager.generate_layout_dict()))
    return construct_json_response({})

def create_widget(widget, import_name, is_loaded=False, position=None, rotation=None, color=None, config=None, rerender=True):
        widget_instance: Widget = widget()
        widget_instance.import_name = import_name
        if is_loaded:
            if position: widget_instance.position = position
            if rotation: widget_instance.rotation = rotation
            if config: 
                for field in config.keys():
                    widget_instance.configuration[field].value = config[field]
        layout_manager.add_widget(widget_instance, color + [255] if color is not None else None)
        if rerender:
            layout_manager.render()

def load_layout_path(file):
    layout_manager.selected_layout_file_path = file
    layout_manager.selected_layout_file_name = file.split("/")[-1]
    with open(layout_manager.selected_layout_file_path) as file:
        layout = json.loads(file.read())

        print("Layout content:", layout)
        layout_manager.remove_all()
        for widget in layout["widgets"]:
            create_widget(widget_manager.widgets[widget["import_name"]], widget["import_name"], True, widget["position"], widget["rotation"], widget["color"], widget["configuration"], rerender=False)
    layout_manager.render()
    matrix_connector.flush_matrix()

@routes.get("/loadlayout")
async def load_layout(request):
    file = filedialpy.openFile(filter="*.mmw", title="Load layout")
    print(file)
    if file:
        load_layout_path(file)
    return construct_full_update()

@routes.get("/setdefaultlayout")
async def set_default_layout(request):
    config.default_layout = layout_manager.selected_layout_file_path
    config.save_config()
    print("Set default to:", layout_manager.selected_layout_file_path)
    return construct_json_response({})

@routes.get("/stop")
async def stop_server(request):
    global running
    running = False
    shutdown()
    return construct_json_response({})

@routes.get("/addtostartup")
async def add_to_startup(request):
    result = "Successfully added to system startup"
    success = True
    try:
        success = platform_specific_functions.add_self_to_startup()
    except PermissionError as e:
        print(e)
        result = "Couldn't write to startup folder (systemd on Linux), run FWMM as root"
    except Exception as e:
        result = "Couldn't add to startup: " + str(e)
    
    if not success:
        result = "An unknown error occurred, check terminal output"
    return construct_json_response({"result": result})

@routes.get("/removefromstartup")
async def remove_from_startup(request):
    result = "Successfully removed from system startup"
    success = True
    try:
        success = platform_specific_functions.remove_self_from_startup()
    except PermissionError:
        result = "Couldn't write to startup folder (systemd on Linux), run FWMM as root"
    except Exception as e:
        result = "Couldn't remove from startup: " + str(e)
    
    if not success:
        result = "An unknown error occurred, check terminal output"
    return construct_json_response({"result": result})

routes.static('/static', get_local_path("static"))

    
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
    print(config, config.default_layout)
    if config.default_layout:
        print("Loading layout:" + config.default_layout)
        load_layout_path(config.default_layout)

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
                raise e
                print("Failed to write to serial:", e)

def main():
    global running, error
    skip_window = "skip-window" in sys.argv
    print("skip window? :", skip_window)


    print(os.system("whoami"))

    error = get_active_ports()

    if not matrix_connector.is_connected():
        print("Couldn't connect to LED matrix:", error)
        running = False
    else:
        print("config")
        load_config()

    app.cleanup_ctx.append(background_tasks)

    print("Starting web server")

    if not skip_window and not DEBUG:
        print("Opening web page")
        webbrowser.open("http://127.0.0.1:5621")

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
            raise e

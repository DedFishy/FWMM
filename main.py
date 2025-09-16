import asyncio
import json
import random
import time
from serial.tools.list_ports import comports
from config import Config
import util
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
import signal

# Recognized by freezer
import font_loader, text_based_widget

def shutdown():
    signal.raise_signal(signal.SIGTERM)

DEBUG = os.path.exists(".debug") # Controls how much error handling to do

running = True # Whether the application is currently active

error = "" # Error encountered during startup (if any)

# Handles the configuration file
config = Config()

# Handles the virtual representation of the matrix's pixel values
matrix_rep = Matrix()
# Handles the connection to the physical matrix
matrix_connector = MatrixConnector(matrix_rep)

def flush_layout_manager():
    """Access point for the layout manager to rerender the layout"""
    matrix_connector.flush_matrix()
# Handles the currently present widgets
layout_manager = LayoutManager(matrix_rep, lambda: flush_layout_manager())

# Handles widgets found in the widgets folder
widget_manager = WidgetManager()

# Handles code that needs to change depending on platform
platform_specific_functions = platform_specific.get_class()

# List of string notifications that the user needs to see
queued_notifications = []

# List all widgets that failed to load (likely due to dependencies)
if len(widget_manager.errors.keys()) > 0:
    queued_notifications.append("Failed to load widgets:\n" + "\n".join([error + ": " + widget_manager.errors[error] for error in widget_manager.errors.keys()]))

# Initialize aiohttp server
app = web.Application()
routes = web.RouteTableDef()

def get_local_path(path: str):
    """Returns a path corrected for when the application is frozen"""
    if platform_specific_functions.is_frozen:
        return "_internal/" + path
    return path

def construct_json_response(dictionary: dict) -> web.Response:
    """Creates an aiohttp response out of a dictionary, encoded as JSON"""
    return web.Response(text=json.dumps(dictionary), content_type="text/json")

def construct_full_update() -> web.Response:
    """Creates a "full update", or all the data that is needed after almost any action"""
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

# Load the frontend files only once if debug mode is off
if not DEBUG:
    with open(get_local_path("index.html"), "r") as index_file:
        html = index_file.read()
    with open(get_local_path("static/fwmm.js"), "r") as fwmm_js:
        js = fwmm_js.read()
    with open(get_local_path("static/style.css"), "r") as css_file:
        css = css_file.read()
    with open(get_local_path("font_maker/index.html"), "r") as font_maker_file:
        font_maker = font_maker_file.read()

# Allows access to the font maker, an HTML document that helps with creating JSON formatted pixel fonts
@routes.get("/font_maker")
async def font_maker(_) -> web.Response:
    if DEBUG:
        with open(get_local_path("font_maker/index.html"), "r") as font_maker_file:
            return web.Response(text=font_maker_file.read(), content_type="text/html")
    return web.Response(text=font_maker, content_type="text/html")

# Access index.html
@routes.get("/")
async def index_handler(_) -> web.Response:
    global error
    if not running:
        error = str(error)
        if "[Errno 13]" in error:
            error = "Permission to access your matrix was denied. Please run 'sudo chmod 666 " + error.split(" ")[-1].replace("'", "") + "' to allow FWMM to connect to your input module."
        with open(get_local_path("static/error.html"), "r") as error_doc:
            return web.Response(body=error_doc.read().replace("[error]", error_doc), content_type="text/html")
    if DEBUG:
        with open(get_local_path("index.html"), "r") as index_file:
            return web.Response(text=index_file.read(), content_type="text/html")
    return web.Response(text=html, content_type="text/html")

# Access fwmm.js
@routes.get("/fwmm.js")
async def js_handler(_) -> web.Response:
    if DEBUG:
        with open(get_local_path("static/fwmm.js"), "r") as fwmm_js:
            return web.Response(text=fwmm_js.read(), content_type="text/javascript")
    return web.Response(text=js, content_type="text/javascript")

# Access style.css
@routes.get("/style.css")
async def css_handler(_) -> web.Response:
    global css
    if DEBUG:
        with open(get_local_path("static/style.css"), "r") as css:
            return web.Response(text=css.read(), content_type="text/css")
    return web.Response(text=css, content_type="text/css")
    
# API Definitions

# Get the initial full update so that the config is reflected
@routes.get("/initial")
async def available_widgets(_) -> web.Response:
    return construct_full_update()

# Create a new widget by name
@routes.get("/createwidget/{widget}")
async def widget_meta(request: web.Request) -> web.Response:
    widget_name = request.match_info.get("widget", None)
    widget: Widget = widget_manager.widgets[widget_name]()
    widget.color = (random.randint(0, 255) for _ in range(3))

    layout_manager.add_widget(widget)

    layout_manager.render()
    matrix_connector.flush_matrix()

    return construct_full_update()

# Edits a config item on a particular widget
@routes.get("/updatewidgetconfig/{widget_index}/{name}/{new_value}")
async def update_widget_config(request: web.Request) -> web.Response:
    widget_index = request.match_info.get("widget_index", None)
    name = request.match_info.get("name", None)
    new_value = request.match_info.get("new_value", None)

    layout_manager.widgets[int(widget_index)].widget.configuration[name].update_value(new_value)

    layout_manager.render()
    matrix_connector.flush_matrix()

    return construct_full_update()

# Edits a widget's color
@routes.get("/updatewidgetcolor/{widget_index}/{new_value}")
async def update_widget_color(request: web.Request) -> web.Response:
    widget_index = request.match_info.get("widget_index", None)
    new_value = request.match_info.get("new_value", None)
    layout_manager.widgets[int(widget_index)].color = tuple(int(new_value.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

    return construct_json_response({})

# Edits a widget's transform properties
@routes.get("/updatewidgettransform/{widget_index}/{name}/{new_value}")
async def update_widget_transform(request: web.Request) -> web.Response:
    widget_index = request.match_info.get("widget_index", None)
    name = request.match_info.get("name", None)
    new_value = request.match_info.get("new_value", None)
    target = layout_manager.widgets[int(widget_index)].widget
    if name == "X": target.position[0] = int(new_value)
    elif name == "Y": target.position[1] = int(new_value)
    elif name == "Rotation": target.rotation = int(new_value)
    else: print("Invalid transform variable:", name)

    layout_manager.render()
    matrix_connector.flush_matrix()

    return construct_full_update()

# Deletes a widget
@routes.get("/deletewidget/{widget_index}")
async def delete_widget(request: web.Request) -> web.Response:
    widget_index = request.match_info.get("widget_index", None)
    layout_manager.remove(layout_manager.widgets[int(widget_index)])
    layout_manager.render()
    matrix_connector.flush_matrix()
    return construct_full_update()

# Flush the LED matrix... NOW!
@routes.get("/updatenow")
async def update_now(_) -> web.Response:
    layout_manager.render()
    matrix_connector.flush_matrix()
    return construct_full_update()

# Save the current layout 
@routes.get("/savelayout")
async def save_layout(_) -> web.Response:
    file = filedialpy.saveFile(filter="*.mmw", title="Save layout")
    if file:
        layout_manager.selected_layout_file_path = file
        layout_manager.selected_layout_file_name = file.split("/")[-1]
        with open(layout_manager.selected_layout_file_path, "w+") as file:
            file.write(json.dumps(layout_manager.generate_layout_dict()))
    return construct_json_response({})

# Load a layout file
@routes.get("/loadlayout")
async def load_layout(_) -> web.Response:
    file = filedialpy.openFile(filter="*.mmw", title="Load layout")
    if file:
        load_layout_path(file)
    return construct_full_update()

# Set the current layout as the default one
@routes.get("/setdefaultlayout")
async def set_default_layout(_) -> web.Response:
    config.default_layout = layout_manager.selected_layout_file_path
    config.save_config()
    return construct_json_response({})

# Shutdown the application
@routes.get("/stop")
async def stop_server(_) -> web.Response:
    global running
    running = False
    shutdown()
    return construct_json_response({})

# Add the application to the laptop's startup sequence
@routes.get("/addtostartup")
async def add_to_startup(_) -> web.Response:
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

# Remove the application from the laptop's startup sequence
@routes.get("/removefromstartup")
async def remove_from_startup(_) -> web.Response:
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

# Make all of the files in the static folder accessible
routes.static('/static', get_local_path("static"))

# Add all routes to the aiohttp application
app.add_routes(routes)

def create_widget(
        widget:      Widget, 
        import_name: str, 
        is_loaded:   bool     =False, 
        position:    bool|None=None, 
        rotation:    bool|None=None, 
        color:       bool|None=None, 
        config:      bool|None=None, 
        rerender:    bool     =True
        ):
        """Construct a new widget and add it to the current layout"""
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

def load_layout_path(file: str):
    """Load a layout from a path"""
    layout_manager.selected_layout_file_path = file
    layout_manager.selected_layout_file_name = file.split("/")[-1]
    with open(layout_manager.selected_layout_file_path) as file_read:
        layout = json.loads(file_read.read())
        layout_manager.remove_all()
        for widget in layout["widgets"]:
            create_widget(widget_manager.widgets[widget["import_name"]], widget["import_name"], True, widget["position"], widget["rotation"], widget["color"], widget["configuration"], rerender=False)
    layout_manager.render()
    matrix_connector.flush_matrix()

# Detected COM ports
ports = {}

def try_connect_matrix(port: str | None) -> Exception|None:
    """Attempt to connect to the LED matrix's COM port"""
    try:
        matrix_connector.connect(port)
    except Exception as e:
        return e

def get_active_ports() -> Exception|None:
    """Get all available COM ports"""
    ports = comports()
    resolved = {}
    for port, desc, hwid in sorted(ports):
        resolved[port] = desc, hwid

    result = "No error recorded"

    # Iterate over COM ports
    for port in resolved.keys():
        # Check if the port is the LED matrix
        if util.eval_is_matrix(resolved[port][1]):
            # Attempt to connect to the matrix
            result = try_connect_matrix(port)
    
    return result

def load_config():
    """Load the data from the configuration file"""
    if config.default_layout:
        # Load default layout if it exists
        load_layout_path(config.default_layout)

async def background_tasks(app):
    """Runs the matrix update loop as an async background task"""
    global running
    # Add matrix update loop to the app, causing it to run
    app["matrix_update_loop"] = asyncio.create_task(
        matrix_update_loop()
    )
    yield
    # Tell matrix update loop to stop
    running = False

    # Cancels the matrix update loop
    app["matrix_update_loop"].cancel()
    # Wait for amtrix update loop to actually exit
    await app["matrix_update_loop"]

async def matrix_update_loop():
    """Updates the LED matrix based on the desired SPF of the widgets in the layout"""
    # Initialize desired Seconds Per Frame (SPF)
    spf = layout_manager.get_desired_spf()
    print("Starting rendering loop at SPF of", spf)
    # Initialize frame start time
    start_time = time.time()
    while running:
        # Allow loop to rest
        await asyncio.sleep(0.1)
        # Get latest SPF
        spf = layout_manager.get_desired_spf()
        
        # Don't update if the widgets don't need to
        if spf == -1: 
            await asyncio.sleep(1)
            continue
        
        # Get the time since the last frame
        seconds_elapsed = time.time() - start_time
        # If the time since last frame is adequate, render an update
        if (seconds_elapsed >= spf):
            # Reset start time
            start_time = time.time()
            print("Rendering next frame")
            try:
                # Render frame and update SPF again
                layout_manager.render()
                matrix_connector.flush_matrix()
                spf = layout_manager.get_desired_spf()
            except Exception as e:
                # Alert that an error occurred before raising it again
                print("Failed to write to serial:", e)
                raise e

def main():
    """Starts up FWMM!"""
    global running, error

    # Determine whether to open FWMM in the browser
    skip_window = "skip-window" in sys.argv

    # Connect to the LED matrix or get an error (usually meaning root is needed on Linux)
    error = get_active_ports()

    if not matrix_connector.is_connected(): # Connection to LED matrix failed
        print("Couldn't connect to LED matrix:", error)
        running = False
    else: # Continue forward!
        load_config()

    # Add the matrix updating loop to the async context
    app.cleanup_ctx.append(background_tasks)

    # Open the interface in a web browser
    if not skip_window and not DEBUG:
        webbrowser.open("http://127.0.0.1:5621")

    # Run the aiohttp server
    web.run_app(app, host="127.0.0.1", port=5621)
    # Tell the matrix loop that we're done
    running = False
    
    # Turn off the LED matrix upon exit
    matrix_connector.set_sleep(True)
    

if __name__ == "__main__":
    # Run without a wrapper on debug mode
    if DEBUG: main()
    else:
        # Run with a wrapper
        try:
            main()
        except Exception as e:
            raise e

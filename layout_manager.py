from typing import Callable
import numpy as np
from matrix import Matrix
from widget import Widget
from widget_layout_object import WidgetObjectLayout

class LayoutManager:
    widgets: list[WidgetObjectLayout] = []
    matrix: Matrix
    flush_callback: Callable

    selected_layout_file_path = ""
    selected_layout_file_name = ""

    def __init__(self, matrix: Matrix, flush_callback: Callable):
        self.matrix = matrix
        self.flush_callback = flush_callback

    def add_widget(self, widget: Widget, color=None):
        widget_object_layout = WidgetObjectLayout(widget, self, color)
        self.widgets.append(widget_object_layout)
        widget_object_layout.create_dpg()
        return widget_object_layout

    def generate_layout_dict(self):
        return {
            "widgets": [
                {
                    "position": widget.widget.position,
                    "rotation": widget.widget.rotation,
                    "color": widget.color,
                    "import_name": widget.widget.import_name, # type: ignore
                    "configuration": {field: widget.widget.configuration[field].value for field in widget.widget.configuration.keys()}
                } for widget in self.widgets
            ]
        }

    def remove_all(self):
        for widget in self.widgets:
            widget.destroy()
        self.widgets = []

    def remove(self, widget):
        self.widgets.remove(widget)
        self.render()
        self.flush_callback()

    def collapse_all(self):
        for widget in self.widgets:
            if widget.showing_config:
                widget.toggle_showing_config()

    def get_desired_spf(self):
        spf = -1
        for widget in self.widgets:
            desired = widget.widget.get_desired_spf()
            #print(desired)
            if desired == -1: desired = 30
            if desired < spf or spf == -1:
                spf = desired
        return spf
    
    def render(self):
        self.matrix.fill(0)
        for widget in self.widgets:
            self.render_widget(widget)

    def render_widget(self, widget: WidgetObjectLayout):
        widget_pixels_untyped: np.matrix|list = widget.widget.get_frame()
        if type(widget_pixels_untyped) == list:
            widget_pixels: np.matrix = np.matrix(widget_pixels_untyped)
        elif type(widget_pixels_untyped) == np.matrix:
            widget_pixels = widget_pixels_untyped

        if widget.widget.allow_rotation and widget.widget.rotation != 0:
            widget_pixels = np.rot90(widget_pixels, widget.widget.rotation // 90) # type: ignore
        

        self.matrix.impose(widget_pixels, widget.widget.position)
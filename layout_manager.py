import numpy as np
from const import HEIGHT, WIDTH
from matrix import Matrix
from widget import Widget
from matrix import Matrix
from widget import Widget
from widget_layout_object import WidgetObjectLayout

class LayoutManager:
    widgets: list[WidgetObjectLayout] = []
    matrix: Matrix = None
    flush_callback = None

    selected_layout_file_path = None
    selected_layout_file_name = None

    def __init__(self, matrix: Matrix, flush_callback):
        self.matrix = matrix
        self.flush_callback = flush_callback

    def add_widget(self, widget: Widget, color=None):
        widget_object_layout = WidgetObjectLayout(widget, self, len(self.widgets), color)
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
                    "import_name": widget.widget.import_name,
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
            print(desired)
            if desired == -1: desired = 30
            if desired < spf or spf == -1:
                spf = desired
        return spf
    
    def render(self):
        self.matrix.fill(0)
        for widget in self.widgets:
            self.render_widget(widget)

    def render_widget(self, widget: WidgetObjectLayout):
        widget_pixels: np.matrix = widget.widget.get_frame()
        if type(widget_pixels) == list:
            widget_pixels = np.matrix(widget_pixels)

        self.matrix.impose(widget_pixels, widget.widget.position)
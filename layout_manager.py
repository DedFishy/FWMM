from matrix import Matrix
from widget import Widget
from matrix import Matrix
from widget import Widget
from widget_layout_object import WidgetObjectLayout

class LayoutManager:
    widgets: list[WidgetObjectLayout] = []
    matrix: Matrix = None
    flush_callback = None

    def __init__(self, matrix: Matrix, flush_callback):
        self.matrix = matrix
        self.flush_callback = flush_callback

    def add_widget(self, widget: Widget):
        print(widget)
        widget_object_layout = WidgetObjectLayout(widget, self, len(self.widgets))
        self.widgets.append(widget_object_layout)
        widget_object_layout.create_dpg()
    
    def render(self):
        self.matrix.fill(0)
        for widget in self.widgets:
            self.render_widget(widget)

    def render_widget(self, widget: WidgetObjectLayout):
        widget_pixels = widget.widget.get_frame()
        for x in range(0, widget.widget.get_current_size()[0]):
            for y in range(0, widget.widget.get_current_size()[1]):
                self.matrix.set_led(widget.widget.position[0]+x, widget.widget.position[1]+y, widget_pixels[y][x])
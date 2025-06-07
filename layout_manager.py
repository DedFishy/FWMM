from matrix import Matrix
from widget import Widget
from matrix import Matrix
from widget import Widget

class LayoutManager:
    widgets: dict[str, Widget] = {}
    matrix: Matrix = None

    def __init__(self, matrix: Matrix):
        self.matrix = matrix

    def add_widget(self, widget: Widget):
        self.widgets.append(widget)
    
    def render(self):
        for widget in self.widgets:
            self.render_widget(widget)

    def render_widget(self, widget: Widget):
        widget_pixels = widget.get_frame()
        for x in range(0, widget.current_size[0]):
            for y in range(0, widget.current_size[1]):
                self.matrix.set_led(widget.position[0]+x, widget.position[1]+y, widget_pixels[y][x])
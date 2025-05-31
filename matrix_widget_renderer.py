from matrix import Matrix
from widget import Widget

class MatrixWidgetRenderer:
    def __init__(self, matrix, widgets = {}):
        self.matrix: Matrix = matrix
        self.widgets: dict[str, Widget] = widgets
    
    def add_widget(self, name, widget):
        self.widgets[name] = widget
    
    def render_widget(self, widget: Widget, position, rotation):
        widget_pixels = widget.get_frame()
        for x in range(0, widget.current_size[0]):
            for y in range(0, widget.current_size[1]):
                self.matrix.set_led(position[0]+x, position[1]+y, widget_pixels[y][x])
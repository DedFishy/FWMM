from tkinter import Canvas
from util import from_rgb
from matrix import Matrix
from const import WIDTH, HEIGHT

ON = ""

class MatrixTk(Canvas):
    def __init__(self, parent, matrix, scale=5):
        Canvas.__init__(self, parent, width=scale*WIDTH, height=scale*HEIGHT, bg="#000000", border=0)
        print(scale * WIDTH, scale * HEIGHT)

        self.matrix_scale = scale

        self.matrix = matrix

        self.setup()
    
    def setup(self):
        pass

    def update_matrix(self):
        self.render_matrix(self.matrix)

    def set_led(self, x, y, value):
        self.matrix.set_led(x, y, value)
        self._draw_led(x, y, value)

    def toggle_led(self, x, y, on_value, off_value):
        if self.matrix.get_led(x, y) == on_value:
            self.set_led(x, y, off_value)
        else:
            self.set_led(x, y, on_value)
        

    def _draw_led(self, x, y, value):
        print(x, y, value)
        print(x*self.matrix_scale, y*self.matrix_scale, 
            (x+1)*self.matrix_scale, (y+1)*self.matrix_scale)
        color_value = from_rgb((value, value, value))
        self.create_rectangle(
            x*self.matrix_scale+2, y*self.matrix_scale+2, 
            (x+1)*self.matrix_scale+2, (y+1)*self.matrix_scale+2,
            fill=color_value, outline=""
        )

    def render_matrix(self, matrix: Matrix):
        x = 0
        y = 0
        for row in matrix.matrix:
            for column in row:
                self._draw_led(x, y, column)
                x += 1
            y += 1
            x = 0
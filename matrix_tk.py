from tkinter import Canvas
from util import from_rgb

WIDTH = 9
HEIGHT = 34

ON = ""

class Matrix(Canvas):
    def __init__(self, parent, scale=5):
        Canvas.__init__(self, parent, width=scale*WIDTH, height=scale*HEIGHT, bg="#000000")

        self.matrix_scale = scale

        self.setup()
    
    def setup(self):
        pass

    def draw_led(self, x, y, value):
        color_value = from_rgb((value, value, value))
        self.create_oval(
            x*self.matrix_scale, y*self.matrix_scale, 
            (x+1)*self.matrix_scale, (y+1)*self.matrix_scale,
            fill=color_value
        )
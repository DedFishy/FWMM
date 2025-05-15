from tkinter import ttk
from util import from_rgb
from matrix import Matrix
from const import WIDTH, HEIGHT

class MatrixWidgetTk(ttk.Frame):
    def __init__(self, parent, scale=5):
        ttk.Frame.__init__(self, parent, width=WIDTH*scale, height=HEIGHT*scale)

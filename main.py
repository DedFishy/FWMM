from matrix_connector import MatrixConnector
from detect import get_active_ports
import sys
import random
import tkinter as tk
from tkinter import ttk
from matrix import Matrix
from matrix_tk import MatrixTk
from matrix_connector import MatrixConnector

class App(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        self.matrix = Matrix()
        self.matrix_connector = MatrixConnector(self.matrix)

        self.setup_widgets()

    def setup_widgets(self):
        # Tab container
        self.tabs = ttk.Notebook(self)

        # Overview tab
        self.overview_tab = ttk.Frame(self.tabs)
        # Overview's matrix
        self.overview_matrix = MatrixTk(self.overview_tab, self.matrix, scale=10)
        self.overview_matrix.grid(row=0, column=1, rowspan=5)
        self.overview_matrix.bind("<Button-1>", self.update_one_led)
        # debug
        self.debug_button = ttk.Button(self.overview_tab, text="debug", command=lambda: self.overview_matrix.toggle_led(random.randint(0, 8), random.randint(0, 33), random.randint(0, 255), 0))
        self.debug_button.grid(row=0, column=0)

        # Pack the overview
        self.tabs.add(self.overview_tab, text='Overview')

        # Pack the tab container
        self.tabs.pack(expand=1, fill="both")

    def update_one_led(self, event):
        self.overview_matrix.toggle_led(int(event.x/self.overview_matrix.matrix_scale), int(event.y/self.overview_matrix.matrix_scale), 255, 0)
        self.matrix_connector.flush_matrix()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Framework Matrix Manager")

    # Simply set the theme
    root.tk.call("source", "azure.tcl")
    root.tk.call("set_theme", "dark")

    app = App(root)
    app.pack(fill="both", expand=True)

    root.update()

    root.mainloop()
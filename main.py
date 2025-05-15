from matrix_connector import MatrixConnector
from detect import get_active_ports
import sys
import random
import tkinter as tk
from tkinter import ttk, font
from matrix import Matrix
from matrix_tk import MatrixTk
from matrix_connector import MatrixConnector

class App(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self)

        self.matrix = Matrix()
        self.matrix_connector = MatrixConnector(self.matrix)

        self.normal_font = font.Font(self, size=16)

        self.setup_widgets()

    def setup_widgets(self):
        # Tab container
        self.tabs = ttk.Notebook(self)

        # Overview tab
        self.overview_tab = ttk.Frame(self.tabs)
        # Overview's matrix
        self.overview_matrix = MatrixTk(self.overview_tab, self.matrix, scale=10)
        self.overview_matrix.grid(row=0, column=1, rowspan=5)
        # debug
        self.debug_button = ttk.Button(self.overview_tab, text="debug", command=lambda: self.overview_matrix.toggle_led(random.randint(0, 8), random.randint(0, 33), random.randint(0, 255), 0))
        self.debug_button.grid(row=0, column=0)

        # Pack the overview
        self.tabs.add(self.overview_tab, text='Overview')

        # Widget tab
        self.widget_tab = ttk.Frame(self.tabs)
        self.widget_tab.grid_columnconfigure(1, weight=1)
        self.widget_tab.grid_columnconfigure(2, weight=1)
        self.widget_tab.grid_rowconfigure(1, weight=1)

        # Layout selector
        self.affix_label(self.widget_tab, 0, 0, "Layout: ")
        self.widget_layout_selector = ttk.Combobox(self.widget_tab, values=["Widgets Numero Uno", "The second one", "Gary."], )
        self.widget_layout_selector.grid(row=0, column=1, columnspan=3, sticky="EW")

        # Widget list
        self.widget_list_container = ttk.Frame(self.widget_tab)
        self.widget_list_container.grid(row=1, column=0, columnspan=2, sticky="NSW")
        self.widget_list_container.grid_rowconfigure(0, weight=1)

        self.widget_list_canvas = tk.Canvas(self.widget_list_container)
        self.widget_list_canvas.grid(row=0, column=1, sticky="NSE")

        self.widget_list_scrollbar = ttk.Scrollbar(self.widget_list_container, command=self.widget_list_canvas.yview)
        self.widget_list_scrollbar.grid(row=0, column=0, sticky="NSW")
        

        self.widget_list_canvas.configure(yscrollcommand = self.widget_list_scrollbar.set)

        # update scrollregion after starting 'mainloop'
        # when all widgets are in canvas
        self.widget_list_canvas.bind('<Configure>', lambda e: self.widget_list_canvas.configure(scrollregion=self.widget_list_canvas.bbox('all')))
        self.widget_list_canvas.bind_all("<MouseWheel>", lambda e: self.widget_list_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self.widget_list = tk.Frame(self.widget_list_canvas)
        self.widget_list_canvas.create_window((0, 0), window=self.widget_list, anchor="nw")

        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        ttk.Label(self.widget_list, text="Among Us").pack()
        
        # Pack the widget tab
        self.tabs.add(self.widget_tab, text="Widgets", sticky="NSEW")

        # Pack the tab container
        self.tabs.pack(expand=1, fill="both")

    def affix_label(self, master, row, column, text, font=None, columnspan=1, rowspan=1):
        if not font: font = self.normal_font
        ttk.Label(master, text=text, font=font).grid(row=row, column=column, columnspan=columnspan, rowspan=rowspan)


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
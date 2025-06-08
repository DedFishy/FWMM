# Framework Matrix Module Manager
A utility to customize what is displayed on your Framework 16 LED matrix module using a widget-based system
## How to use:
- Install pyserial, dearpygui and numpy
- Run main.py
- Connect to your matrix if it is not automatically connected
- Add widgets to your layout!

Note: For now, this is only guaranteed to work on Windows. I change operating systems often, so it will probably recieve Linux support in no time.

## Creating new widgets:
The builtin widgets are not super customizable. To make a new one:
- Create a new Python file in the widgets folder
- Create a class named Widget that is a subclass of the Widget class in widget.py
- Fill out required fields and create the functions that will render the widget and inform of size changes
- Run main.py and add your new widget to a layout!
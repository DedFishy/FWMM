# Framework Matrix Manager
A utility to customize what is displayed on your Framework 16 LED matrix module using a widget-based system

## Running
### Windows:
Simply download the latest release from the [GitHub Releases](https://github.com/DedFishy/FWMM/releases), extract the ZIP file, and run `FWMM.exe`.
### Linux:
You will need to run the source code directly (for now).
- Install the [dependencies](#dependencies)
- Download [the source code as a ZIP file](https://github.com/DedFishy/FWMM/archive/refs/heads/main.zip)
- Extract the ZIP file
- Run `main.py` with the Python you installed the dependencies to
NOTE: Linux support is currently experimental (until I switch to Linux again)

## Usage
When launching the program, you will be met with a window. The software will automatically find your LED matrix (only one is supported right now because I only have one).
### Layouts
All of your customizations will live inside a "layout" file, which has a `.mmw` file extension but is really just a JSON file.
You may load or save your layouts as this, and setting a default layout will cause that layout to be loaded whenever you start FWMM.


Note: For now, this is only guaranteed to work on Windows. I change operating systems often, so it will probably recieve Linux support in no time.

## Dependencies
- `pyserial`
- `dearpygui`
- `plyer`
- `pillow`
- `numpy`
- `pystray`
- `pywinctl`
On Windows:
- `winshell`

## Creating new widgets:
The builtin widgets are not super customizable. To make a new one:
- Create a new Python file in the widgets folder
- Create a class named Widget that is a subclass of the Widget class in widget.py
- Fill out required fields and create the functions that will render the widget and inform of size changes
- Run main.py and add your new widget to a layout!
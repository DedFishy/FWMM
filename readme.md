# [Framework Matrix Manager](https://boyne.dev/projects/fwmm.html)
![Demonstrative Photo](https://github.com/DedFishy/dedfishy.github.io/blob/main/assets/projects/fwmm/screen_and_matrix.jpg?raw=true)
A utility to customize what is displayed on your Framework 16 LED matrix module using a widget-based system.

## Running
### From Source (for Windows or Linux):
Download the source code from the latest GitHub release and read the instructions there: [GitHub Releases](https://github.com/DedFishy/FWMM/releases)
### Linux Binary:
Download the Linux zip file from the latest GitHub release and run "FWMM": [GitHub Releases](https://github.com/DedFishy/FWMM/releases)

## Usage
When launching the program, your web browser should open to the dashboard. If it doesn't, visit [http://127.0.0.1:5621](http://127.0.0.1:5621).
Here's an overview of what each section of the application does.
### Layout
All of your customizations will live inside a "layout" file, which has a `.mmw` file extension but is really just a JSON file.
You may load or save your layouts as this, and setting a default layout will cause that layout to be loaded whenever you start FWMM again.
### Control
`Stop`: This is where you can stop FWMM, which will turn off your LED matrix.
`Add/Remove from Startup`: Clicking these will register FWMM to either your Linux crontab or your Windows startup folder. This feature will allow FWMM to start whenever you log into your computer. You must set a default layout to use this feature, or your matrix will display nothing!
`Render Now`: This button skips the rendering update loop and renders whatever is on your matrix. This is for if FWMM gets put in a weird state where it does not automatically render things.
### Widgets
To add a widget to the active layout, drag it over from the rightmost pane into the middle pane. It will appear there, and you can configure it as you wish.
Every widget in your layout will appear in the leftmost pane as a colored rectangle. You can customize the color of this rectangle with the widget's color selector, and it will persist.

## Dependencies
- `filedialpy`
- `pyserial`
- `aiohttp`
- `numpy`

On Linux:
- `python_crontab`

On Windows:
- `winshell`

## Creating new widgets
- Create a new Python file in the widgets folder
- Create a class named Widget that is a subclass of the Widget class in widget.py
- Fill out required fields and create the functions that will render the widget and inform of size changes
- Run main.py and add your new widget to a layout!
There is a template for this under `template.py` in the root of this repository.

## Other
If you find a bug, please open a GitHub issue and/or contribute a pull request to fix it.

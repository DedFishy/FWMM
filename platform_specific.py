import os
from pathlib import Path
import sys

class PlatformSpecificFunctions:
    def __init__(self): pass

    def add_self_to_startup(self): pass

class Windows(PlatformSpecificFunctions):
    startup_location = ""
    def __init__(self):
        import winshell
        self.startup_location = winshell.startup()

    def add_self_to_startup(self):
        with open(os.path.join(self.startup_location, "FWMM.bat"), "w+") as startup_script:
            script = "@echo off"
            script += "\ncd " + str(Path(os.path.abspath(__file__)).parent.resolve())
            script += "\nstart " + str(Path(sys.executable).parent.resolve()) + "/pythonw.exe main.py skip-window"
            startup_script.write(script)

def get_class() -> PlatformSpecificFunctions:
    if os.name == "nt": return Windows()
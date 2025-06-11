import os
from pathlib import Path
import sys

import util

class PlatformSpecificFunctions:
    def __init__(self): pass

    def add_self_to_startup(self): pass

class Windows(PlatformSpecificFunctions):
    startup_location = ""
    is_frozen = False
    def __init__(self):
        import winshell
        self.startup_location = winshell.startup()
        self.is_frozen = getattr(sys, 'frozen', False)
    
    def get_self_start_command(self):
        if self.is_frozen:
            return str(Path(sys.executable).resolve())
        else:
            return str(Path(sys.executable).parent.resolve()) + "/pythonw.exe main.py"

    def add_self_to_startup(self):
        with open(os.path.join(self.startup_location, "FWMM.bat"), "w+") as startup_script:
            script = "@echo off"
            script += "\ncd " + str(Path(os.path.abspath(__file__)).parent.resolve())
            script += "\nstart " + self.get_self_start_command() + " skip-window"
            startup_script.write(script)

def get_class() -> PlatformSpecificFunctions:
    if os.name == "nt": return Windows()
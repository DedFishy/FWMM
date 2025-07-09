import os
from pathlib import Path
import sys

import util

class PlatformSpecificFunctions:
    is_frozen = False
    def __init__(self): pass

    def add_self_to_startup(self): pass

    def remove_self_from_startup(self): pass

class Windows(PlatformSpecificFunctions):
    startup_location = ""
    is_frozen = False
    def __init__(self):
        import winshell # type: ignore
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
        return True

    def remove_self_from_startup(self):
        Path(os.path.join(self.startup_location, "FWMM.bat")).unlink(True)
        return True

class Linux(PlatformSpecificFunctions):
    startup_location = ""
    is_frozen = False
    def __init__(self):
        self.startup_location = "/etc/systemd/system"
        self.is_frozen = getattr(sys, 'frozen', False)
    
    def get_self_start_command(self):
        if self.is_frozen:
            return str(Path(sys.executable).resolve())
        else:
            return str(Path(sys.executable).parent.resolve()) + "/python main.py"
    
    def get_working_directory(self):
        if self.is_frozen:
            return str(Path(os.path.abspath(__file__)).parent.parent.resolve())
        return str(Path(os.path.abspath(__file__)).parent.resolve())

    def add_self_to_startup(self):
        with open(os.path.join(self.startup_location, "fwmm.service"), "w+") as startup_script:
            script = "[Unit]"
            script += "\nDescription=Framework Matrix Manager service"
            script += "\n[Service]"
            script += "\nType=simple"
            script += "\nRemainAfterExit=yes"
            script += "\nWorkingDirectory=" + self.get_working_directory()
            script += "\nExecStart=" + self.get_self_start_command() + " skip-window"
            script += "\nRestart=always"
            script += "\nTimeoutStartSec=0"
            script += "\nEnvironment=PYTHONUNBUFFERED=1"
            script += "\n[Install]"
            script += "\nWantedBy=multi-user.target"
            startup_script.write(script)

        success = (os.system("systemctl daemon-reload") + os.system("systemctl enable fwmm.service") == 0)
        return success

    def remove_self_from_startup(self):
        success = (os.system("systemctl disable fwmm.service") + os.system("systemctl daemon-reload") == 0)

        Path(os.path.join(self.startup_location, "fwmm.service")).unlink(True)
        return success


def get_class() -> PlatformSpecificFunctions:
    if os.name == "nt": return Windows()
    elif os.name == "posix": return Linux()
    else: raise OSError("Invalid OS: " + os.name)

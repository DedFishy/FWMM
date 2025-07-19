import os
from pathlib import Path
import sys

class PlatformSpecificFunctions:
    """Functions that need to be specific for which platform FWMM is running on"""
    is_frozen = False
    def __init__(self): pass

    def add_self_to_startup(self):
        """Add FWMM to the laptop's startup sequence"""
        pass

    def remove_self_from_startup(self):
        """Remove FWMM from the laptop's startup sequence"""
        pass

class Windows(PlatformSpecificFunctions):
    """Functions specific to Windows systems"""
    startup_location = ""
    is_frozen = False
    def __init__(self):
        import winshell # type: ignore
        self.startup_location = winshell.startup()
        self.is_frozen = getattr(sys, 'frozen', False)
    
    def get_self_start_command(self):
        """Get the command that needs to be added to the startup batch file"""
        if self.is_frozen:
            return str(Path(sys.executable).resolve())
        else:
            return str(Path(sys.executable).parent.resolve()) + "/pythonw.exe main.py"

    def add_self_to_startup(self) -> bool:
        with open(os.path.join(self.startup_location, "FWMM.bat"), "w+") as startup_script:
            script = "@echo off"
            script += "\ncd " + str(Path(os.path.abspath(__file__)).parent.resolve())
            script += "\nstart " + self.get_self_start_command() + " skip-window"
            startup_script.write(script)
        return True

    def remove_self_from_startup(self) -> bool:
        Path(os.path.join(self.startup_location, "FWMM.bat")).unlink(True)
        return True

class Linux(PlatformSpecificFunctions):
    """Functions specific to Cron-enabled Linux systems"""
    startup_location = ""
    is_frozen = False
    def __init__(self):
        self.startup_location = "/etc/systemd/user"
        self.is_frozen = getattr(sys, 'frozen', False)
    
    def get_self_start_command(self):
        """Get the command that needs to be added to the startup crontab"""
        if self.is_frozen:
            return str(Path(sys.executable).resolve())
        else:
            return str(Path(sys.executable).parent.resolve()) + "/python main.py"
    
    def get_working_directory(self):
        """Get FWMM's current working directory"""
        if self.is_frozen:
            return str(Path(os.path.abspath(__file__)).parent.parent.resolve())
        return str(Path(os.path.abspath(__file__)).parent.resolve())

    def add_self_to_startup(self) -> bool:
        self.remove_self_from_startup() # Prevent duplicates
        from crontab import CronTab
        cron = CronTab(user=True)
        job = cron.new(command=f"cd '{self.get_working_directory()}' && {self.get_self_start_command()} skip-window", comment="FWMM")
        job.every_reboot()
        cron.write()
        return True

    def remove_self_from_startup(self) -> bool:
        from crontab import CronTab
        cron = CronTab(user=True)
        jobs = cron.find_comment("FWMM")
        for job in jobs:
            cron.remove(job)
        cron.write()
        return True


def get_class() -> PlatformSpecificFunctions:
    """Get the correct version of PlatformSpecificFunctions for the current system"""
    if os.name == "nt": return Windows()
    elif os.name == "posix": return Linux()
    else: raise OSError("Invalid OS: " + os.name)

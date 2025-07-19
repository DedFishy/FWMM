import json

class Config:
    """Handles reading, writing, and formatting the configuration file"""
    
    default_layout = None

    def __init__(self):
        try:
            with open("config.json", "x") as file:
                print("Created config file")
                file.write("{}")
        except FileExistsError:
            print("Configuration file found")
        self.read_config()
    
    def read_config(self):
        """Reads the config.json file"""
        with open("config.json", "r") as config_file:
            config_text = config_file.read()
            try:
                config = json.loads(config_text)
                self.default_layout = config["default_layout"]
            except Exception as e:
                print("Failed to load configuration:", e)
    
    def save_config(self):
        """Writes the config.json file"""
        with open("config.json", "w+") as config_file:
            config_file.write(json.dumps({
                "default_layout": self.default_layout
            }))
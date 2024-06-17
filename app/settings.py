import locale
import os

class ApplicationConfiguration():
    def __init__(self):
        
        # values from file
        self.locale = "UA" if locale.getdefaultlocale()[0] == "uk_UA" else "EN"
        self.theme = "darkly"
        self.cache_save = 0
        self.auto_update = 0
        self.cmd = 0


        self.app_name = "ImgProPlus"
        self.version = "1.0.1"

        self.seconds_to_wait = 1

        file_path = os.path.dirname(os.path.realpath(__file__)) + "\\configs\\user_settings"
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    key, value = line.strip().split(":")
                    setattr(self, key.strip(), value.strip())
        else:
            settings_dictionary = {
                        "locale": "EN",
                        "cmd" : 0,
                        "theme" : "darkly",
                        "auto_update" : 0,
                        "cache_save" : 1
                        }
            os.mkdir(os.path.dirname(os.path.realpath(__file__)) + "\\configs")
            with open(file_path, 'w') as file:
                for key, element in settings_dictionary.items():
                    file.write(f"{key}:{element}\n")

                

    def print_config(self):
        for key, value in self.__dict__.items():
            print(f"{key}: {value}")
 




STYLE = {
    "REGISTER_FONT": ("Calibri", "20"),
    "AUTH_FONT": ("Calibri", "20")
}

APP_INIT = {
   "APP_NAME": "ImgProPlus",
   "VERSION": "1.0.1"
}

SERV_IP = {"IP": "127.0.0.1", "PORT": 65432}

# basic text style
TEXT_BASIC_STYLE = 0

# serv address

if __name__ == '__main__':
    conf = ApplicationConfiguration()
    conf.print_config()
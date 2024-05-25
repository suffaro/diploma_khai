from login_page import LoginPage
from app import MainPage
import ttkbootstrap as ttk
from settings import *
import os
from client import Client
from settings import ApplicationConfiguration, APP_INIT


# login 
# rapperorwhat@gmail.com 
# Suma1l24_

class Application(ttk.Window):
    def __init__(self):
        super().__init__()
        try:
            self.title(f"{APP_INIT['APP_NAME']}_v{APP_INIT['VERSION']}")
            self.geometry = ('900x600')
            self.minsize(600,600)
            self.maxsize(1400,1000)
            self.settings = ApplicationConfiguration()
           # self.logger = 
            self.current_theme = self.settings.theme
            self.style.theme_use(self.current_theme)
            self.main_page = MainPage(self)
            if os.getenv("IMG_PLUS"):
                client = Client()
                result = client.process_request(f"TKN|{os.getenv('IMG_PLUS').split(sep='|')[1]}")
                if result == "True":
                    self.main_page.pack(expand=True, fill='both')
            else:
                login_page = LoginPage(self)
                login_page.pack(expand=True, fill='both')

            self.mainloop()
        except ConnectionRefusedError:
            print("No connection to server")


if __name__ == '__main__':
    Application()
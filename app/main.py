from login_page import LoginPage
from app import MenuApp
import ttkbootstrap as ttk
from settings import *
import os
from client import Client
from settings import ApplicationConfiguration, APP_INIT
from ttkbootstrap.dialogs import Messagebox
import sys
from my_logger import setup_logger

if not os.path.exists(os.path.dirname(os.path.realpath(__file__)) + "\\logs"):
    os.mkdir(os.path.dirname(os.path.realpath(__file__)) + "\\logs")
logger = setup_logger(logger_name="User Application", logger_file=".\logs\logs.log")

EXE = False 
try:
    with open(os.path.dirname(os.path.realpath(__file__)) + "\\configs\\token", 'r') as f:
        token = f.read()
except FileNotFoundError:
    token = None

if token is not None and token != "":
    token = token.strip('\n')
else:
    token = None


# login 
# rapperorwhat@gmail.com 
# Suma1l24_

class Application(ttk.Window):
    def __init__(self):
        super().__init__()
        try:
            self.title(f"{APP_INIT['APP_NAME']}_v{APP_INIT['VERSION']}")
            self.geometry = ('1920x600')
            self.minsize(600,600)
            self.maxsize(1920,1080)
            self.settings = ApplicationConfiguration()
            self.current_theme = self.settings.theme
            self.style.theme_use(self.current_theme)
            self.login_page = None
            if token is not None:
                client = Client()
                result = client.process_request(f"TKN|{token.split(sep='|')[1]}")
                if result == "True":
                    self.form_main_page()
                else:
                    Messagebox.show_error("Something wrong with your token! Please login again.", "Error!")
                    os.remove(os.path.dirname(os.path.realpath(__file__)) + "\\configs\\token")
                    self.destroy()
            else:
                self.login_page = LoginPage(self)
                self.login_page.pack(expand=True, fill='both')
            self.mainloop()
        except ConnectionRefusedError:
            Messagebox.ok("No connection to server!", "Connection error!")
        except Exception as e:
            logger.error(f"Something wrong. Error - {e}")
            Messagebox.show_error("Something wrong. Please, try again", "Error!")

    def form_main_page(self):
        if self.login_page:
            self.login_page.pack_forget()
            self.login_page = None
        self.main_page = MenuApp(self) #MainPage(self)
        self.main_page.pack(expand=True, fill='both')

    def restart_app(self):
        self.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == '__main__':
    try:
        if EXE:
            # unpack data txt
            data = ['artists.txt', 'flavors.txt', 'mediums.txt', 'movements.txt', 'negative.txt']
            for elem in data:
                packed_path = resource_path(f"files\{elem}")
                new_path = os.getcwd() + "\data" | elem
                with open(new_path, 'w') as file:
                    with open (packed_path, 'r') as packed_file:
                        file.writelines(packed_file.readlines)
        Application()
    except Exception as e:
        Messagebox.show_error(f"Error - {e}", "Error in app.")


    

    
# todo 
# exe implementation
# mb progressbar (not sure)
# cmd block output
# ADMIN APP
# PAYMENT
#
#
#
#
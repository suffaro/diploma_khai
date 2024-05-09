import locale

APP_NAME = "ImgGayPro"
VERSION = "v1.0"
LOCALE = "UA" if locale.getdefaultlocale()[0] == "uk_UA" else "EN"
SECONDS_TO_WAIT = 1

# heading style
REGISTER_FONT = AUTH_FONT = ("Calibri", "20")


# basic text style
TEXT_BASIC_STYLE = 0


# serv address
SERV_IP = {"IP": "127.0.0.1", "PORT": 65432}
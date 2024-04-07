from settings import *
from localization import LOGIN_PAGE
import ttkbootstrap as ttk
import tkinter as tk
import darkdetect
from slide_widget import SlideWidget
import re

class LoginPage(ttk.Window):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME}_{VERSION}")
        self.geometry = ('900x600')
        self.minsize(600,600)
        self.maxsize(1200,900)
        self.resizable(True, True)


        self.current_theme = "darkly" if darkdetect.isDark() else "journal"
        self.style.theme_use(self.current_theme)

        self.page = LoginFrame(self)
        self.page.pack(expand = True, fill = 'both')

        self.mainloop()


class LoginFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

       # self.animated_notification = SlideWidget(self, 1.0, 0.7)

        #grid
        self.rowconfigure(0, 
                                           weight = 2,
                                           uniform = 'a')
        self.rowconfigure((1,2,3,4,5), 
                                           weight = 1,
                                           uniform = 'a')
        self.rowconfigure(6, 
                                           weight = 1,
                                           uniform = 'a')
        self.columnconfigure(0,
                                           weight = 2,
                                           uniform = 'a')
        self.columnconfigure(1,
                                           weight = 3,
                                           uniform = 'a')
        self.columnconfigure(2,
                                           weight = 2,
                                           uniform = 'a')


        # variables
        self.email_variable = tk.StringVar()
        self.password_variable = tk.StringVar()


        # widgets

        self.auth_label = ttk.Label(self, 
                                  text = LOGIN_PAGE["auth_label"][LOCALE],
                                  anchor = 'center',
                                  font = AUTH_FONT)
        self.auth_label.grid(column = 1,
                        row = 0,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)

        self.login_label = ttk.Label(self, 
                                   text = LOGIN_PAGE["login_label"][LOCALE],
                                   anchor = 'center')
        self.login_label.grid(column = 0,
                        row = 1,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)

        self.login_entry = ttk.Entry(self)
        self.login_entry.grid(column = 1,
                        row = 1,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)
        self.login_entry.focus_force()

        self.password_label = ttk.Label(self, 
                                    text = LOGIN_PAGE["password_label"][LOCALE],
                                    anchor = 'center')
        self.password_label.grid(column = 0,
                        row = 2,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)

        
        self.login_entry = ttk.Entry(self)
        self.login_entry.grid(column = 1,
                        row = 2,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)

        self.login_button = ttk.Button(self,
                                  text = LOGIN_PAGE["login_button"][LOCALE],
                                  command = self.login_to_app)
        self.login_button.grid(column = 1,
                        row = 3,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)

        self.forgot_password_label = ttk.Label(self,
                                          text = LOGIN_PAGE['forgot_password_label'][LOCALE],
                                          anchor = 'center')
        self.forgot_password_label.grid(column = 1,
                        row = 4,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10,)

        self.new_user_label = ttk.Label(self,
                                   text = LOGIN_PAGE['new_user_label'][LOCALE],
                                   anchor = 'center')
        self.new_user_label.grid(column = 1,
                        row = 5,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10,
                        )       

        self.registration_button = ttk.Button(self,
                                  text = LOGIN_PAGE["registration_button"][LOCALE],
                                  command = lambda: RegistrationWindow(self),
                                  )
        self.registration_button.place(relx = 0.5,
                                       rely = 0.87,
                                       anchor = 'center',
                                       relheight = 0.06,
                                       relwidth = 0.2)
        
    def login_to_app(self):
        # logic of checking password with server
        self.master.destroy()
        pass




class RegistrationWindow(ttk.Toplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Registration Window")
        self.geometry = ('900x700')
        self.minsize(600,600)
        self.maxsize(1000,600)
        self.resizable(True, True)

        self.email_variable = tk.StringVar()
        self.password_variable = tk.StringVar()
        self.password_repeat_variable = tk.StringVar()
        self.confirmation_code_variable = tk.StringVar()
        

        self.rep = None # var for typing check

        self.rowconfigure(0, 
                                           weight = 2,
                                           uniform = 'a')
        self.rowconfigure((1,2,3,4), 
                                           weight = 1,
                                           uniform = 'a')
        self.rowconfigure(5, 
                                           weight = 2,
                                           uniform = 'a')
        self.rowconfigure(6, 
                                           weight = 2,
                                           uniform = 'a')
        self.columnconfigure(0,
                                           weight = 2,
                                           uniform = 'a')
        self.columnconfigure(1,
                                           weight = 3,
                                           uniform = 'a')
        self.columnconfigure(2,
                                           weight = 2,
                                           uniform = 'a')
        
        

        # variables for widgets


        # adding traces 
        self.email_variable.trace_add('write', self.typing_email)
        self.password_repeat_variable.trace_add('write', self.typing_second_password)


        # auth_heading = ttk.Label(self,
        #                        text = LOGIN_PAGE["mail_label"][LOCALE],
        #                        anchor = 'center')
        # auth_heading.grid(column = 1,
        #                 row = 0,
        #                 sticky = 'nsew',
        #                 padx = 10,
        #                 pady = 10)

        # widgets

        # self.animated_notification = SlideWidget(self, 1.0, 0.7)

        self.wrong_email_label = ttk.Label(self, text = LOGIN_PAGE['wrong_email_label'][LOCALE], anchor = 'ne')
        self.mail_label = ttk.Label(self,
                               text = LOGIN_PAGE["mail_label"][LOCALE],
                               anchor = 'center')
        self.mail_label.grid(column = 0,
                        row = 1,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)


        self.mail_entry = ttk.Entry(self,
                               textvariable = self.email_variable)
        self.mail_entry.grid(column = 1,
                        row = 1,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)
        self.mail_entry.focus_force()
        
        self.password_label = ttk.Label(self, 
                                    text = LOGIN_PAGE["password_label"][LOCALE],
                                    anchor = 'center')
        self.password_label.grid(column = 0,
                        row = 2,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)

        self.password_entry = ttk.Entry(self,
                                   show='*',
                                    textvariable = self.password_variable)
        self.password_entry.grid(column = 1,
                        row = 2,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)

        self.password_repeat_label = ttk.Label(self, 
                                    text = LOGIN_PAGE["password_repeat_label"][LOCALE],
                                    anchor = 'center')
        self.password_repeat_label.grid(column = 0,
                        row = 3,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)

        self.password_repeat_entry = ttk.Entry(self,
                                          show='*',
                                          textvariable = self.password_repeat_variable)
        self.password_repeat_entry.grid(column = 1,
                        row = 3,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)


        self.confirmation_code_label = ttk.Label(self, 
                                    text = LOGIN_PAGE["confirmation_code_label"][LOCALE],
                                    anchor = 'center')
        self.confirmation_code_label.grid(column = 0,
                        row = 4,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)

        self.confirmation_code_entry = ttk.Entry(self,
                                            textvariable = self.confirmation_code_variable,
                                            state = 'disabled'
                                            )
        self.confirmation_code_entry.grid(column = 1,
                        row = 4,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)

        self.registration_button = ttk.Button(self,
                                  text = LOGIN_PAGE["send_confirm_code"][LOCALE],
                                  command = lambda: self.send_confirm_code(email = self.email_variable.get()))
        self.registration_button.grid(column = 1,
                        row = 5,
                        padx = 10,
                        pady = 10)

        self.return_button = ttk.Button(self,
                                  text = LOGIN_PAGE["return_button"][LOCALE],
                                  command = lambda: self.destroy()
                                  )
        self.return_button.place(relx = 0.1,
                            rely = 0.9,
                            anchor = 'center')
        
        self.transient(master) # set to be on top of the main window
        self.grab_set()

        master.wait_window(self)
        

    # listeners for entries        
    def validate_email(self, *args) -> None:
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b' # regex for email
        
        if(re.fullmatch(email_regex, self.email_variable.get())):
            print("valid email")
            self.mail_entry.configure(bootstyle = 'success')
        else:
            print('cringe email..')
            self.mail_entry.configure(bootstyle = 'danger')
            self.wrong_email_label.grid(column = 2, row = 1)

        self.rep = None
        
    def typing_email(self, *args) -> None:
        if self.rep is None:
            print("typing email...")
            self.wrong_email_label.grid_forget()
            self.mail_entry.configure(bootstyle = 'primary')
        else:
            self.after_cancel(self.rep)
        
        self.rep = self.after(SECONDS_TO_WAIT * 1000, self.validate_email)
       
    def send_confirm_code(self, email) -> None:
        print(email)
        pass

    def typing_second_password(self, *args) -> None:
        if self.rep is None:
            print("typing second password...")
            self.wrong_email_label.grid_forget()
            self.mail_entry.configure(bootstyle = 'primary')
        else:
            self.after_cancel(self.rep)

        self.rep = self.after(SECONDS_TO_WAIT * 1000, self.validate_second_password)

    def validate_second_password(self, *args) -> None:
        if self.password_variable.get() != self.password_repeat_variable.get():
            print("Passwords are not the same!")
        else:
            print("passwords are same")

        self.rep = None




class ForgotPasswordWindow(ttk.Toplevel):
    def __init__(self, master):
        super().__init__(master)





if __name__ == '__main__':
    LoginPage()
from settings import *
from localization import LOGIN_PAGE
import ttkbootstrap as ttk
import tkinter as tk
import darkdetect
from slide_widget import SlideWidget
from client import Client
import re
from addons import hash_password


class LoginPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master = master)


        self.change_theme_button = ttk.Button(self,
                                              text = "Theme",
                                              command = self.change_current_theme)

        self.current_theme = self.master.current_theme
        # self.style.theme_use(self.current_theme)

        self.change_theme_button.place(relx = 0.9, rely = 0.1, anchor = 'center')
        self.change_theme_button.lift()

        self.grip = ttk.Sizegrip(self)
        self.grip.place(relx=1.0, rely=1.0, anchor="se")
        

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

        self.login_email_entry = ttk.Entry(self,
                                           textvariable=self.email_variable)
        self.login_email_entry.grid(column = 1,
                        row = 1,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)
        self.login_email_entry.focus_force()

        self.password_label = ttk.Label(self, 
                                    text = LOGIN_PAGE["password_label"][LOCALE],
                                    anchor = 'center')
        self.password_label.grid(column = 0,
                        row = 2,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)

        
        self.login_password_entry = ttk.Entry(self,
                                              textvariable=self.password_variable,
                                              show="*")
        self.login_password_entry.grid(column = 1,
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

        self.forgot_password_button = ttk.Button(self,
                                          text = LOGIN_PAGE['forgot_password_button'][LOCALE],
                                          command = lambda: ForgotPasswordWindow(self))
        self.forgot_password_button.grid(column = 1,
                        row = 4,
                        #sticky = 'nsew',
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
        
    def change_current_theme(self):
        if self.current_theme == 'darkly':
            self.current_theme = 'journal'
            self.master.style.theme_use(self.current_theme)
        else:
            self.current_theme = 'darkly'
            self.master.style.theme_use(self.current_theme)
        
    def login_to_app(self):
        client = Client()
        verification = client.process_request(f"UCV|{self.email_variable.get()}|{self.password_variable.get()}")
        if verification == "False":
            print("No login for you dawg")
        else:
            print("Your token - ", end="")
            print(verification)
            self.destroy()
            self.master.main_page.pack(expand=True, fill='both')


class ValidationEntry(ttk.Entry):
    def __init__(self, master, entry_type, notification_handler, text_variable, second_password_variable=None):
        super().__init__(master=master, textvariable=text_variable)
        self.entry_type = entry_type
        self.notification = notification_handler

        self.rep = None

        self.second_password_variable = second_password_variable if second_password_variable else None

        #self.entry_config()
        print()

    def entry_config(self) -> None:
        if self.entry_type == 'login':
            self.textvariable.trace_add('write', self.typing_email)
        elif self.entry_type == 'uno_password':
            self.textvariable.trace_add('write', self.typing_password)
        elif self.entry_type == 'duo_password':
            self.textvariable.trace_add('write', self.typing_second_password)


    def check_password(password):
    # Check if password length is at least 8 characters
        if len(password) < 8:
            return False
        
        # Define regular expressions for each character type
        uppercase_regex = r'[A-Z]'
        lowercase_regex = r'[a-z]'
        digit_regex = r'\d'
        symbol_regex = r'[!@#$%^&*()-_+=~`[\]{}|;:,.<>?]'
        
        # Count the number of character types present in the password
        types_count = 0
        if re.search(uppercase_regex, password):
            types_count += 1
        if re.search(lowercase_regex, password):
            types_count += 1
        if re.search(digit_regex, password):
            types_count += 1
        if re.search(symbol_regex, password):
            types_count += 1
        
        # Check if at least two character types are present
        if types_count >= 2:
            return True
        else:
            return False

    def validate_password(self, *args) -> None:
        
        if self.check_password(self.textvariable.get()):
            print("valid password")
            self.configure(bootstyle = 'success')
        else:
            self.notification.show_message("Passwords must have at least 8 characters and contain at least two of the following: uppercase letters, lowercase letters, numbers, and symbols")
            print('cringe password..')
            self.configure(bootstyle = 'danger')

        self.rep = None
        
    def typing_password(self, *args) -> None:
        if self.rep is None:
            self.notification.destroy_message()
            print("typing password...")
            self.configure(bootstyle = 'primary')
        else:
            self.after_cancel(self.rep)
        
        self.rep = self.after(SECONDS_TO_WAIT * 1000, self.validate_password)


    # functions for email verification
    def validate_email(email) -> bool:
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b' # regex for email
        
        if re.fullmatch(email_regex, email):
            return True
        else:
            return False

        
    def typing_email(self, *args) -> None:
        if self.rep is None:
            self.notification.destroy_message()
            print("typing email...")
            self.configure(bootstyle = 'primary')
        else:
            self.after_cancel(self.rep)
        
        self.rep = self.after(SECONDS_TO_WAIT * 1000, self.validate_email)
        
    def typing_second_password(self, *args) -> None:
        if self.rep is None:
            print("typing second password...")
            self.configure(bootstyle = 'primary')
        else:
            self.after_cancel(self.rep)

        self.rep = self.after(SECONDS_TO_WAIT * 1000, self.validate_second_password)

    def validate_second_password(self, *args) -> None:
        if self.text_variable.get() != self.second_password_variable.get():
            self.configure(bootstyle = 'danger')
            self.notification.show_message("Passwords must match!")
            print("Passwords are not the same!")
        else:
            print("passwords are same")
            self.configure(bootstyle = 'success')

        self.rep = None



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
        

        self.writing_listener = None # var for typing check

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
        # self.email_variable.trace_add('write', typing_email)
        # self.password_repeat_variable.trace_add('write', typing_second_password)
        # self.password_variable.trace_add('write', typing_password)


        # auth_heading = ttk.Label(self,
        #                        text = LOGIN_PAGE["mail_label"][LOCALE],
        #                        anchor = 'center')
        # auth_heading.grid(column = 1,
        #                 row = 0,
        #                 sticky = 'nsew',
        #                 padx = 10,
        #                 pady = 10)

        # widgets

        self.notification = SlideWidget(self)

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
    
    # def validate_password(self, *args) -> None:
        
    #     if check_password(self.password_variable.get()):
    #         print("valid password")
    #         self.password_entry.configure(bootstyle = 'success')
    #     else:
    #         self.notification.show_message("Passwords must have at least 8 characters and contain at least two of the following: uppercase letters, lowercase letters, numbers, and symbols")
    #         print('cringe password..')
    #         self.password_entry.configure(bootstyle = 'danger')

    #     self.rep = None
        
    # def typing_password(self, *args) -> None:
    #     if self.rep is None:
    #         self.notification.destroy_message()
    #         print("typing password...")
    #         self.password_entry.configure(bootstyle = 'primary')
    #     else:
    #         self.after_cancel(self.rep)
        
    #     self.rep = self.after(SECONDS_TO_WAIT * 1000, self.validate_password)


    # def validate_email(self, *args) -> None:
    #     email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b' # regex for email
        
    #     if re.fullmatch(email_regex, self.email_variable.get()):
    #         print("valid email")
    #         self.mail_entry.configure(bootstyle = 'success')
    #     else:
    #         self.notification.show_message("Wrong type of email!")
    #         print('cringe email..')
    #         self.mail_entry.configure(bootstyle = 'danger')


    #     self.rep = None
        
    # def typing_email(self, *args) -> None:
    #     if self.rep is None:
    #         self.notification.destroy_message()
    #         print("typing email...")
    #         self.wrong_email_label.grid_forget()
    #         self.mail_entry.configure(bootstyle = 'primary')
    #     else:
    #         self.after_cancel(self.rep)
        
    #     self.rep = self.after(SECONDS_TO_WAIT * 1000, self.validate_email)
       

    # def typing_second_password(self, *args) -> None:
    #     if self.rep is None:
    #         print("typing second password...")
    #         self.password_repeat_entry.configure(bootstyle = 'primary')
    #     else:
    #         self.after_cancel(self.rep)

    #     self.rep = self.after(SECONDS_TO_WAIT * 1000, self.validate_second_password)

    # def validate_second_password(self, *args) -> None:
    #     if self.password_variable.get() != self.password_repeat_variable.get():
    #         self.password_repeat_entry.configure(bootstyle = 'danger')
    #         self.notification.show_message("Passwords must match!")
    #         print("Passwords are not the same!")
    #     else:
    #         print("passwords are same")
    #         self.password_repeat_entry.configure(bootstyle = 'success')

    #     self.rep = None


    def send_confirm_code(self, email) -> None:
        client = Client()
        print(email)
        pass




class ForgotPasswordWindow(ttk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title('Password restoration')
        self.geometry('500x300')
        self.minsize(500, 300)
        self.maxsize(1000, 600)

        self.notification = SlideWidget(self)

        # variable declaration
        self.login_variable = ttk.StringVar()
        self.new_password_variable = ttk.StringVar()
        self.new_password_repeat_variable = ttk.StringVar()
        self.confirmation_code_variable = ttk.StringVar()


        # callbacks for hints

       # email_function = self.register(validate_email)


        # confirmation code frame
        self.confirmation_code_frame = ttk.Frame(self)

        self.confirmation_code_frame.columnconfigure((0,1,2), weight=1)
        self.confirmation_code_frame.rowconfigure((0,1,2,3), weight=1)

        confirmation_sent_label = ttk.Label(self.confirmation_code_frame,
                                            text = LOGIN_PAGE["forgot_window_confirmation_code_label"][LOCALE])
        confirmation_sent_label.grid(row = 0, column = 1)

        confirmation_code_entry = ttk.Entry(self.confirmation_code_frame,)
        confirmation_code_entry.grid(row = 1, column = 1, sticky='ew')

        confirm_code_button = ttk.Button(self.confirmation_code_frame,
                                         text = LOGIN_PAGE["forgot_window_confirmation_code_button"][LOCALE],
                                         command = self.check_confirmation_password,
                                         default = 'active') # do it in client i guess
        
        confirm_code_button.grid(row = 2, column = 1)
        
        # input login frame

        self.input_login_frame = ttk.Frame(self)

        self.input_login_frame.columnconfigure((0,1,2), weight=1)
        self.input_login_frame.rowconfigure((0,1,2,3), weight=1)

        self.user_input_email_label = ttk.Label(self.input_login_frame,
                                            text = LOGIN_PAGE["forgot_window_user_email_label"][LOCALE])
        self.user_input_email_label.grid(row = 0, column = 1)

        self.user_input_email_entry = ttk.Entry(self.input_login_frame,
                                           textvariable = self.login_variable,
                                           bootstyle = 'success',
                                           validate = 'focus',
                                           validatecommand=(email_function, '%s'))
        self.user_input_email_entry.grid(row = 1, column = 1, sticky='ew')

        self.send_code_button = ttk.Button(self.input_login_frame,
                                         text = LOGIN_PAGE["forgot_window_user_email_button"][LOCALE],
                                         command = lambda : self.send_confirmation_code(self.login_variable.get()),
                                         state = 'disabled',
                                         ) # do it in client i guess
        
        self.send_code_button.grid(row = 2, column = 1)

        # create new password frame




        # binds
        self.user_input_email_entry.bind('<Configure>', self.activate_send_email_button)

        

        # return button 
        
        self.return_button = ttk.Button(self,
                                  text = LOGIN_PAGE["return_button"][LOCALE],
                                  command = lambda: self.destroy()
                                  )
        self.return_button.place(relx = 0.1,
                            rely = 0.9,
                            anchor = 'center')

        self.input_login_frame.pack(expand=True, fill='both')


    
        self.transient(master) # set to be on top of the main window
        self.grab_set()

        master.wait_window(self)

    def send_confirmation_code(self, username: str):
        client = Client()
        client
        self.input_login_frame.pack_forget()
        self.confirmation_code_frame.pack(expand=True, fill='both')

    def activate_send_email_button(self, event: object):
        print(self.user_input_email_entry.cget('style'))
        self.send_code_button['state'] = 'active'



    


    def check_confirmation_password(self):
        self.confirmation_code_frame.pack_forget()





if __name__ == '__main__':
    master = ttk.Window()
    master.current_theme = 'darkly'
    LoginPage(master).pack(expand=True, fill='both')
    master.mainloop()
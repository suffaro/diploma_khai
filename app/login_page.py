from settings import ApplicationConfiguration, STYLE
from localization import LOGIN_PAGE, MESSAGES
import ttkbootstrap as ttk
from slide_widget import SlideWidget
from client import Client
import re
from ttkbootstrap.dialogs import Messagebox
from my_logger import setup_logger
import os, sys
from pathlib import Path
import threading    



SECONDS_TO_WAIT = 1

app_configuration = ApplicationConfiguration()
if not os.path.exists(os.path.dirname(os.path.realpath(__file__)) + "\\logs"):
    os.mkdir(os.path.dirname(os.path.realpath(__file__)) + "\\logs")
logger = setup_logger(logger_name="User Application", logger_file=".\logs\logs.log")

class LoginPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master = master)



        self.change_theme_button = ttk.Button(self,
                                              text = LOGIN_PAGE["theme_button"][app_configuration.locale],
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
        self.email_variable = ttk.StringVar()
        self.password_variable = ttk.StringVar()


        # widgets



        self.auth_label = ttk.Label(self, 
                                  text = LOGIN_PAGE["auth_label"][app_configuration.locale],
                                  anchor = 'center',
                                  font = STYLE['AUTH_FONT'])
        self.auth_label.grid(column = 1,
                        row = 0,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)

        self.login_label = ttk.Label(self, 
                                   text = LOGIN_PAGE["login_label"][app_configuration.locale],
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
                                    text = LOGIN_PAGE["password_label"][app_configuration.locale],
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

        # for event
        self.msgbox_checker_wrong = [None]
        self.login_button = ttk.Button(self,
                                  text = LOGIN_PAGE["login_button"][app_configuration.locale],
                                  command = lambda: threading.Thread(target = self.login_to_app, args=(self.msgbox_checker_wrong,)).start(),)
        self.login_button.grid(column = 1,
                        row = 3,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)

        self.forgot_password_button = ttk.Button(self,
                                          text = LOGIN_PAGE['forgot_password_button'][app_configuration.locale],
                                          command = lambda: ForgotPasswordWindow(self))
        self.forgot_password_button.grid(column = 1,
                        row = 4,
                        #sticky = 'nsew',
                        padx = 10,
                        pady = 10,)

        self.new_user_label = ttk.Label(self,
                                   text = LOGIN_PAGE['new_user_label'][app_configuration.locale],
                                   anchor = 'center')
        self.new_user_label.grid(column = 1,
                        row = 5,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10,
                        )       

        self.registration_button = ttk.Button(self,
                                  text = LOGIN_PAGE["registration_button"][app_configuration.locale],
                                  command = lambda: RegistrationWindow(self, [self]),
                                  )
        self.registration_button.place(relx = 0.5,
                                       rely = 0.87,
                                       anchor = 'center',
                                       relheight = 0.06,
                                       relwidth = 0.2)
        
        self.checker_event = self.after(1000, self.login_verification_event)
        
        
    def change_current_theme(self):
        if self.current_theme == 'darkly':
            self.current_theme = 'journal'
            self.master.style.theme_use(self.current_theme)
        else:
            self.current_theme = 'darkly'
            self.master.style.theme_use(self.current_theme)
        
    def login_verification_event(self, cancel=False, *args):
        if self.msgbox_checker_wrong[0] == False:
            Messagebox.show_error(LOGIN_PAGE["message_wrong_email_or_pass"][app_configuration.locale], "Error", parent=self)
            self.msgbox_checker_wrong[0] = None
        elif self.msgbox_checker_wrong[0]:
            self.after_cancel(self.checker_event)

        self.after(1000, self.login_verification_event)

            


    def login_to_app(self, checker):
        client = Client()
        verification = client.process_request(f"UCV|{self.email_variable.get()}|{self.password_variable.get()}")
        if verification == "False":
            checker[0] = False
        else:
            checker[0] = True
            with open(os.path.dirname(os.path.realpath(__file__)) + "\\configs\\token", 'w') as f:
                f.write(f"{self.email_variable.get()}|{verification}")
            self.master.form_main_page()



class ValidationEntry(ttk.Entry):
    def __init__(self, master, entry_type, notification_handler, text_variable, show=None, second_password_variable=None):
        super().__init__(master=master, textvariable=text_variable, show=show)
        self.entry_type = entry_type
        self.notification = notification_handler

        self.rep = [None, None]

        self.textvariable = text_variable

        self.second_password_variable = second_password_variable if second_password_variable else None

        self.entry_config()

    def entry_config(self) -> None:
        if self.entry_type == 'login':
            self.textvariable.trace_add('write', self.typing_email)
        elif self.entry_type == 'uno_password':
            self.textvariable.trace_add('write', self.typing_password)
        elif self.entry_type == 'duo_password':
            self.textvariable.trace_add('write', self.typing_second_password)


    def check_password(self, password) -> bool:
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
            self.configure(bootstyle = 'success')
            self.rep = [None, True]
        else:
            self.notification.show_message(LOGIN_PAGE['password_validation_error'][app_configuration.locale])
            self.configure(bootstyle = 'danger')
            self.rep = [None, None]

        
    def typing_password(self, *args) -> None:
        if self.rep[0] is None:
            self.notification.destroy_message()
            self.configure(bootstyle = 'primary')
        else:
            self.after_cancel(self.rep)
        
        self.rep = self.after(SECONDS_TO_WAIT * 1000, self.validate_password)


    # functions for email verification
    def validate_email(self) -> None:
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b' # regex for email
        
        if re.fullmatch(email_regex, self.textvariable.get()):
            self.configure(bootstyle = 'success')
            self.rep = [None, True]
        else:
            self.notification.show_message(LOGIN_PAGE['email_validation_error'][app_configuration.locale])
            self.configure(bootstyle = 'danger')
            self.rep = [None, None]
        
        

        
    def typing_email(self, *args) -> None:
        if self.rep[0] is None:
            self.notification.destroy_message()
            self.configure(bootstyle = 'primary')
        else:
            self.after_cancel(self.rep)
        
        self.rep = self.after(SECONDS_TO_WAIT * 1000, self.validate_email)

        
    def typing_second_password(self, *args) -> None:
        if self.rep[0] is None:
            self.notification.destroy_message()
            self.configure(bootstyle = 'primary')
        else:
            self.after_cancel(self.rep)

        self.rep = self.after(SECONDS_TO_WAIT * 1000, self.validate_second_password)

    def validate_second_password(self, *args) -> None:
        if self.textvariable.get() != self.second_password_variable.get():
            self.configure(bootstyle = 'danger')
            self.notification.show_message("Passwords must match!")
            self.rep = [None, None]

        else:
            self.configure(bootstyle = 'success')
            self.rep = [None, True]




class RegistrationWindow(ttk.Toplevel):
    def __init__(self, master, reference_variable):
        super().__init__(master=master)

        self.title(LOGIN_PAGE["registration_title"][app_configuration.locale])
        self.geometry = ('900x700')
        self.minsize(600,600)
        self.maxsize(1000,600)
        self.resizable(True, True)

        self.email_variable = ttk.StringVar()
        self.password_variable = ttk.StringVar()
        self.password_repeat_variable = ttk.StringVar()
        self.confirmation_code_variable = ttk.StringVar()
        

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

        self.notification = SlideWidget(self)

        self.wrong_email_label = ttk.Label(self, text = LOGIN_PAGE['wrong_email_label'][app_configuration.locale], anchor = 'ne')
        self.mail_label = ttk.Label(self,
                               text = LOGIN_PAGE["mail_label"][app_configuration.locale],
                               anchor = 'center')
        self.mail_label.grid(column = 0,
                        row = 1,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)


        self.mail_entry = ValidationEntry(master = self,
                                entry_type = 'login',
                                notification_handler = self.notification,
                                text_variable = self.email_variable
                               )
        self.mail_entry.grid(column = 1,
                        row = 1,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)
        self.mail_entry.focus_force()
        
        self.password_label = ttk.Label(self, 
                                    text = LOGIN_PAGE["password_label"][app_configuration.locale],
                                    anchor = 'center')
        self.password_label.grid(column = 0,
                        row = 2,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)

        self.password_entry = ValidationEntry(master = self,
                                entry_type = 'uno_password',
                                notification_handler = self.notification,
                                text_variable = self.password_variable,
                                show="*"
                               )
        self.password_entry.grid(column = 1,
                        row = 2,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)

        self.password_repeat_label = ttk.Label(self, 
                                    text = LOGIN_PAGE["password_repeat_label"][app_configuration.locale],
                                    anchor = 'center')
        self.password_repeat_label.grid(column = 0,
                        row = 3,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)

        self.password_repeat_entry = ValidationEntry(master = self,
                                entry_type = 'duo_password',
                                notification_handler = self.notification,
                                text_variable = self.password_repeat_variable,
                                second_password_variable = self.password_variable,
                                show="*"
                               )
        self.password_repeat_entry.grid(column = 1,
                        row = 3,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)


        self.confirmation_code_label = ttk.Label(self, 
                                    text = LOGIN_PAGE["confirmation_code_label"][app_configuration.locale],
                                    anchor = 'center')
        self.confirmation_code_label.grid(column = 0,
                        row = 4,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)

        self.confirmation_code_entry = ttk.Entry(self,
                                            textvariable = self.confirmation_code_variable,
                                            state = 'disabled',
                                            bootstyle = 'dark'
                                            )
        self.confirmation_code_entry.grid(column = 1,
                        row = 4,
                        sticky = 'nsew',
                        padx = 10,
                        pady = 10)

        self.registration_button = ttk.Button(self,
                                  text = LOGIN_PAGE["send_confirm_code"][app_configuration.locale],
                                  command = lambda: self.send_confirm_code(email = self.email_variable.get()),
                                  state='disabled')
        self.registration_button.grid(column = 1,
                        row = 5,
                        padx = 10,
                        pady = 10)

        self.return_button = ttk.Button(self,
                                  text = LOGIN_PAGE["return_button"][app_configuration.locale],
                                  command = lambda: self.destroy()
                                  )
        self.return_button.place(relx = 0.1,
                            rely = 0.9,
                            anchor = 'center')
        
        self.transient(master) # set to be on top of the main window
        self.grab_set()

        self.after(0, self.validate_entries)

        master.wait_window(self)
        
    def validate_entries(self):
        if all([
            self.mail_entry.rep[1] == True,
            self.password_entry.rep[1] == True,
            self.password_repeat_entry.rep[1] == True
        ]):
            self.registration_button.configure(state='enabled')
        else:
            self.registration_button.configure(state='disabled')

        self.after(SECONDS_TO_WAIT * 1200, self.validate_entries)

        # After a short delay, re-validate the entries


    def send_confirm_code(self, email) -> None:
        try:
            client = Client()
            result = client.process_request(f"CLS|{email}")
            if result != "True":
                Messagebox.show_error(LOGIN_PAGE["email_already_taken_message"][app_configuration.locale], LOGIN_PAGE["email_already_taken_message_title"][app_configuration.locale])
                return
            conf_code = client.process_request(f"SCC|{email}")
            if conf_code != "send":
                Messagebox.show_error(conf_code, "Error during registration.")
                return
            else:
                Messagebox.ok(LOGIN_PAGE["code_sent_message"][app_configuration.locale], LOGIN_PAGE["code_sent_message_title"][app_configuration.locale])
            self.registration_button.configure(text = LOGIN_PAGE["button_confirm_code"][app_configuration.locale])
            self.confirmation_code_entry.configure(state = 'enabled')
            self.confirmation_code_entry.configure(bootstyle = 'default')
            self.registration_button.configure(command = self.verify_confirm_code)
        except Exception as e:
            logger.error("Error happened - {e}")
            Messagebox.okcancel(MESSAGES["unhandled_exception"][app_configuration.locale], "Error during registration")
            

    def verify_confirm_code(self) -> None:
        try:
            client = Client()
            result = client.process_request(f"VCC|{self.email_variable.get()}|{self.confirmation_code_variable.get()}")
            if result == "True":
                Messagebox.ok(LOGIN_PAGE["code_approved_msg"][app_configuration.locale], LOGIN_PAGE["code_approved_msg_title"][app_configuration.locale])
            else:
                Messagebox.show_error(LOGIN_PAGE["code_not_approved_msg"][app_configuration.locale], LOGIN_PAGE["code_not_approved_msg_title"][app_configuration.locale])
                return    

            
            token = client.process_request(f"REG|{self.email_variable.get()}|{self.password_variable.get()}")
            if token == "done":
                answer = Messagebox.okcancel(LOGIN_PAGE["user_registered_msg"][app_configuration.locale], LOGIN_PAGE["user_registered_msg_title"][app_configuration.locale])
                if answer:
                    token = client.process_request(f"UCV|{self.email_variable.get()}|{self.password_variable.get()}")
                    with open(os.path.dirname(os.path.realpath(__file__)) + "\\configs\\token", 'w') as f:
                        f.write(f"{self.email_variable.get()}|{token}")
                    self.master.master.form_main_page()
                    self.destroy()
                else:
                    self.destroy()

            elif result == 'confirm_wrong':
                Messagebox.show_error("Wrong confirmation password. Please check it again, or contact QA using address imgproplus@gmail.com.", "Error during registration.")
            else:
                Messagebox.show_error(f"Error during confirmation code. {e}", "Error during registration.")
        except Exception as e:
            logger.error(f"Something wrong during confirmation code. Error - {e}")
            Messagebox.show_error(f"Error during confirmation code. {e}", "Error during registration.")

            
        




class ForgotPasswordWindow(ttk.Toplevel):
    def __init__(self, master):
        super().__init__(master=master)
        self.title(LOGIN_PAGE["recover_password_title"][app_configuration.locale])
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
                                            text = LOGIN_PAGE["forgot_window_confirmation_code_label"][app_configuration.locale])
        confirmation_sent_label.grid(row = 0, column = 1)

        confirmation_code_entry = ttk.Entry(self.confirmation_code_frame, textvariable=self.confirmation_code_variable)
        confirmation_code_entry.grid(row = 1, column = 1, sticky='ew')

        confirm_code_button = ttk.Button(self.confirmation_code_frame,
                                         text = LOGIN_PAGE["forgot_window_confirmation_code_button"][app_configuration.locale],
                                         command = self.check_confirmation_code,
                                         default = 'active') # do it in client i guess
        
        confirm_code_button.grid(row = 2, column = 1)
        
        # input login frame

        self.input_login_frame = ttk.Frame(self)

        self.input_login_frame.columnconfigure((0,1,2), weight=1)
        self.input_login_frame.rowconfigure((0,1,2,3), weight=1)

        self.user_input_email_label = ttk.Label(self.input_login_frame,
                                            text = LOGIN_PAGE["forgot_window_user_email_label"][app_configuration.locale])
        self.user_input_email_label.grid(row = 0, column = 1)

        self.user_input_email_entry = ValidationEntry(master=self.input_login_frame,
                                           entry_type = 'login',
                                           notification_handler = self.notification,
                                           text_variable = self.login_variable
                                           )
        
        self.user_input_email_entry.grid(row = 1, column = 1, sticky='ew')

        self.send_code_button = ttk.Button(self.input_login_frame,
                                         text = LOGIN_PAGE["forgot_window_user_email_button"][app_configuration.locale],
                                         command = lambda : self.send_confirmation_code(self.login_variable.get()),
                                         state = 'disabled',
                                         ) # do it in client i guess
        
        self.send_code_button.grid(row = 2, column = 1)

        # create new password frame
        self.new_password_frame = ttk.Frame(self)

        self.new_password_frame.columnconfigure((0,1,2), weight=1)
        self.new_password_frame.rowconfigure((0,1,2,3), weight=1)

        new_password_label = ttk.Label(self.new_password_frame,
                                       text = LOGIN_PAGE["password_label"][app_configuration.locale])
        new_password_label.grid(row = 0, column = 1)

        new_password_entry = ValidationEntry(master=self.new_password_frame,
                                            entry_type = 'uno_password',
                                            notification_handler = self.notification,
                                            text_variable = self.new_password_variable,
                                            show="*"
                                            )
        new_password_entry.grid(row = 1, column = 1, sticky='ew')

        new_password_repeat_label = ttk.Label(self.new_password_frame,
                                              text = LOGIN_PAGE["password_repeat_label"][app_configuration.locale])
        new_password_repeat_label.grid(row = 2, column = 1)

        new_password_repeat_entry = ValidationEntry(master=self.new_password_frame,
                                            entry_type = 'duo_password',
                                            notification_handler = self.notification,
                                            text_variable = self.new_password_repeat_variable,
                                            second_password_variable = self.new_password_variable,
                                            show="*"
                                            )
        new_password_repeat_entry.grid(row = 3, column = 1, sticky='ew')

        # add here button 

        self.send_password_button = ttk.Button(self.new_password_frame,
                                  text = LOGIN_PAGE["send_password_button"][app_configuration.locale],
                                  command = self.create_new_password)
        self.send_password_button.grid(row = 4,
                            column = 1, 
                            sticky='ew',
                            pady = 5
                            )

        # binds
        self.user_input_email_entry.bind('<Configure>', self.activate_send_email_button)

        

        # return button 
        
        self.return_button = ttk.Button(self,
                                  text = LOGIN_PAGE["return_button"][app_configuration.locale],
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
        result = client.process_request(f"CLS|{username}")
        if result == "True":
            Messagebox.show_error(LOGIN_PAGE["email_doesnt_exist_msg"][app_configuration.locale], LOGIN_PAGE["email_doesnt_exist_msg_title"][app_configuration.locale])
            return
        answer = client.process_request(f"SCC|{username}")
        if answer == "send":
            self.input_login_frame.pack_forget()
            self.confirmation_code_frame.pack(expand=True, fill='both')
            self.username = username
        else:
            Messagebox.show_error(LOGIN_PAGE["wrong_confirmation_code_msg"][app_configuration.locale], LOGIN_PAGE["wrong_confirmation_code_msg_title"][app_configuration.locale], parent=self)
        

    def activate_send_email_button(self, event: object):
        self.send_code_button['state'] = 'active'


    def create_new_password(self) -> None:
        if self.new_password_variable.get() == self.new_password_repeat_variable.get():
            client = Client()
            answer = client.process_request(f"RES|{self.username}|{self.new_password_variable.get()}")
            if answer == "True":
                Messagebox.show_info(LOGIN_PAGE["password_changed_successfully"][app_configuration.locale], LOGIN_PAGE["password_changed_successfully_title"][app_configuration.locale], parent=self)
                self.destroy()
            else:
                Messagebox.show_error(LOGIN_PAGE["error_changing_password"][app_configuration.locale], LOGIN_PAGE["error_changing_password_title"][app_configuration.locale], parent=self)
        else:
            Messagebox.show_error(LOGIN_PAGE["passwords_dont_match"][app_configuration.locale], LOGIN_PAGE["passwords_dont_match_title"][app_configuration.locale], parent=self)


    def check_confirmation_code(self):
        client = Client()
        answer = client.process_request(f"VCC|{self.login_variable.get()}|{self.confirmation_code_variable.get()}")
        if answer == "True":
            self.confirmation_code_frame.pack_forget()
            self.new_password_frame.pack(expand=True, fill='both')
        else:
            Messagebox.show_error(LOGIN_PAGE["wrong_confirmation_code_msg"][app_configuration.locale], LOGIN_PAGE["wrong_confirmation_code_msg_title"][app_configuration.locale], parent=self)




def send_logs(error) -> None:
    answer = Messagebox.okcancel("You encountered ")



if __name__ == '__main__':
    master = ttk.Window()
    master.current_theme = 'darkly'
    LoginPage(master).pack(expand=True, fill='both')
    master.mainloop()
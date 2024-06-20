from settings import ApplicationConfiguration, APP_INIT
from localization import MAIN_WINDOW, CLOSE_BUTTON
import ttkbootstrap as ttk
from PIL import Image, ImageTk, ImageSequence
from tkinter import filedialog, Canvas
from addons import get_gpus, get_processor_name
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.constants import INFO, INVERSE
import os
from client import Client
from login_page import ForgotPasswordWindow
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.scrolled import ScrolledText
from addons import Config
import threading
from pathlib import Path
from itertools import cycle
import time
import pyperclip
import tkinterweb
from my_logger import setup_logger
import qrcode
import qrcode.image.pil
import sys

sys.path.insert(0, '..\\clip')


CAPTION_MODELS = {
    'blip-base': 'Salesforce/blip-image-captioning-base',   # 990MB
    'blip-large': 'Salesforce/blip-image-captioning-large', # 1.9GB
    'blip2-2.7b': 'Salesforce/blip2-opt-2.7b',              # 15.5GB
    'blip2-flan-t5-xl': 'Salesforce/blip2-flan-t5-xl',      # 15.77GB
    'git-large-coco': 'microsoft/git-large-coco',           # 1.58GB
}

app_configuration = ApplicationConfiguration()
if not os.path.exists(os.path.dirname(os.path.realpath(__file__)) + "\\logs"):
    os.mkdir(os.path.dirname(os.path.realpath(__file__)) + "\\logs")
logger = setup_logger(logger_name="User Application", logger_file=".\logs\logs.log")



class MenuApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master = master)
        global USERNAME

        try:
            with open(os.path.dirname(os.path.realpath(__file__)) + "\\configs\\token", 'r') as f:
                token = f.read()
        except FileNotFoundError:
            token = None

        self.frame_container = ttk.Frame(self)
        self.frame_container.pack_propagate(0)

        if token is not None:
            logger.info(f"User: {token.split(sep='|')[0]}")
            USERNAME = token.split(sep='|')[0]
        else:
            USERNAME = None
        self.frames = {
            MAIN_WINDOW['notebook_mainpage_tab'][app_configuration.locale]: MainTab(self.frame_container), #MainTab(self.frame_container),
            MAIN_WINDOW['notebook_extensions_tab'][app_configuration.locale]: ExtensionsTab(self.frame_container),
            MAIN_WINDOW['notebook_qa_tab'][app_configuration.locale]: SendQuestionTab(self.frame_container),
            MAIN_WINDOW['notebook_docs_tab'][app_configuration.locale]: DocumentationTab(self.frame_container),
            MAIN_WINDOW['notebook_settings_tab'][app_configuration.locale]: SettingsTab(self.frame_container),
            MAIN_WINDOW['notebook_account_tab'][app_configuration.locale]: AccountTab(self.frame_container),
                       }
        self.create_widgets()

    def create_widgets(self):
        # Menu frame at the top
        menu_frame = ttk.Frame(self)
        menu_frame.pack(side='top', fill='x')
        
        # Container frame to hold the different content frames        
        # Dictionary to store the content frames
        self.frame_container.pack(expand=True, fill='both')

        
        # List of menu buttons and corresponding frame content
        buttons = [
            (MAIN_WINDOW['notebook_mainpage_tab'][app_configuration.locale], self.create_frame1),
            (MAIN_WINDOW['notebook_extensions_tab'][app_configuration.locale], self.create_frame2),
            (MAIN_WINDOW['notebook_qa_tab'][app_configuration.locale], self.create_frame3),
            (MAIN_WINDOW['notebook_docs_tab'][app_configuration.locale], self.create_frame4),
            (MAIN_WINDOW['notebook_settings_tab'][app_configuration.locale], self.create_frame5),
            (MAIN_WINDOW['notebook_account_tab'][app_configuration.locale], self.create_frame6)
        ]
        
        # Create buttons
        for text, frame_func in buttons:
            button = ttk.Button(menu_frame, text=text, command=frame_func, bootstyle='info')
            button.pack(side='left', padx=1, pady=2, fill='x', expand=True)

        # Initialize with the first frame
        #self.pack_propagate(0)
        self.create_frame1()

    def create_frame1(self):
        self.show_frame(MAIN_WINDOW['notebook_mainpage_tab'][app_configuration.locale])

    def create_frame2(self):
        self.show_frame(MAIN_WINDOW['notebook_extensions_tab'][app_configuration.locale])

    def create_frame3(self):
        self.show_frame(MAIN_WINDOW['notebook_qa_tab'][app_configuration.locale])

    def create_frame4(self):
        self.show_frame(MAIN_WINDOW['notebook_docs_tab'][app_configuration.locale])

    def create_frame5(self):
        self.show_frame(MAIN_WINDOW['notebook_settings_tab'][app_configuration.locale])

    def create_frame6(self):
        self.show_frame(MAIN_WINDOW['notebook_account_tab'][app_configuration.locale])

    def show_frame(self, frame_name):
        # Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()
        
        # Create the frame if it doesn't exist
        
        # Show the requested frame
        self.frames[frame_name].pack(expand=True, fill='both')



class AccountTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        # what can user see in account tab?
        # amount of credits
        # subscription status
        # login
        # ability to change password
        # button to logout
        # buy subscription button

        # dotenv.load_dotenv()


        self.columnconfigure((0,4), weight=1, uniform='a')
        self.columnconfigure((1,2), weight=4, uniform='a')
        self.rowconfigure((0,1,2,3,4), weight=1, uniform='a')

        self.username = USERNAME

        self.username_label_name = ttk.Label(self,
                                             text = MAIN_WINDOW["username_label"][app_configuration.locale])
        self.username_label_name.grid(column=1, row=0, sticky='nsew')


        self.username_label = ttk.Label(self,
                                        text = self.username)
        self.username_label.grid(column=2, row=0, sticky='nsew')

        # subscription
        self.subscription_status_label = ttk.Label(self,
                                                   text = MAIN_WINDOW["subscription_label"][app_configuration.locale])
        self.subscription_status_label.grid(column=1, row=1, sticky='nsew')

        self.subscription_status_variable = subscription_status_verification()
        self.subscription_status = ttk.Label(self)
        if self.subscription_status_variable == "No":
            self.subscription_status['text'] = MAIN_WINDOW['sub_status_no'][app_configuration.locale]
        else:
            self.subscription_status['text'] = f"{MAIN_WINDOW['sub_status_yes'][app_configuration.locale]} (up to {self.subscription_status_variable})"
        self.subscription_status.grid(row = 1, column = 2, sticky='nsew')

        # credits
        self.credit_status_label = ttk.Label(self,
                                                   text = MAIN_WINDOW["credit_label"][app_configuration.locale])
        self.credit_status_label.grid(column=1, row=2, sticky='nsew')

        self.credit_status_variable = self.credit_status_verification(self.username)
        self.credit_status = ttk.Label(self, 
                                             text = self.credit_status_variable)
        self.credit_status.grid(row = 2, column = 2, sticky='nsew')

        # logout button

        self.logout_button = ttk.Button(self,
                                        text=MAIN_WINDOW["logout_button"][app_configuration.locale],
                                        command=self.logout)
        self.logout_button.grid(row = 4, column = 2, sticky='ew', padx=4)

        # change password button

        self.change_password_button = ttk.Button(self,
                                        text=MAIN_WINDOW["change_password_button"][app_configuration.locale],
                                        command= lambda: ForgotPasswordWindow(self))
        self.change_password_button.grid(row = 4, column = 1, sticky='ew', padx=4)

        # buy subscription button

        self.purchase_subscription_button = ttk.Button(self,
                                        text=MAIN_WINDOW["purchase_subscription_button"][app_configuration.locale],
                                        command= lambda: PaymentWindow(self.master, True))
        self.purchase_subscription_button.grid(row = 3, column = 2, sticky='ew', padx=4)




    def logout(self) -> None:
        client = Client()
        respond = client.process_request(f"RMV|{self.username}")
        if respond == "True":
            Messagebox.ok("You have successfully logged out!", "Logout")
            os.remove(os.path.dirname(os.path.realpath(__file__)) + "\\configs\\token")
            os.remove(os.path.dirname(os.path.realpath(__file__)) + "\\configs\\user_settings")
            self.master.master.master.destroy()
        else:
            Messagebox.show_error("Something went wrong!", "Logout")     


    def credit_status_verification(self, username) -> str:
        if self.subscription_status_variable != 'No':
            return "∞" #MAIN_WINDOW["unlimited_credits_label"][app_configuration.locale]
        else:
            client = Client()
            result = client.process_request(f"CSV|{username}")
            return result



class MainTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.master = master
        self.PICTURE_EXISTS = False
        self.image = None
        self.image_file = None

        self.config_file = Config()

        if app_configuration.cmd:
            self.config_file.quiet = False
        else:
            self.config_file.quiet = True

        self.columnconfigure(0, weight=4, uniform='a')
        self.columnconfigure(1, weight=3, uniform='a')
        self.rowconfigure(0, weight=4, uniform='a')
        self.rowconfigure(1, weight=1, uniform='a')


        self.upload_image_frame = ttk.Frame(self,
                                )
        self.upload_image_frame.columnconfigure(0, weight=1, uniform='a',)
        self.upload_image_frame.rowconfigure(0, weight=1, uniform='a')

        
        self.upload_button = ttk.Button(self,
                                        text = MAIN_WINDOW['upload_image_button'][app_configuration.locale], # change for app_configuration.locales
                                        command=self.upload_image)
        
        self.upload_button.place(relx = 0.3,
                                rely = 0.4,
                                anchor = 'center',
                                )


        self.upload_image_frame.grid(row = 0, column = 0, sticky='nsew')

        
        # widgets for image_frame

        self.canvas_for_image = Canvas(self.upload_image_frame, 
                                      height=200, 
                                      width=200, 
                                      borderwidth=0, 
                                      highlightthickness=0, 
                                      relief='ridge')
        self.canvas_for_image.grid(row = 0, column = 0, sticky = 'nsew', padx=0, pady=0)
        
        self.canvas_for_image.bind('<Configure>', self.stretch_image)
        self.canvas_for_image.bind('<Configure>', self.fill_image)

        # widgets for settings_frame

        self.settings_frame = ttk.Frame(self,)

        self.settings_device_variable = ttk.StringVar()
        self.settings_model_variable = ttk.StringVar()
        self.settings_model_mode_variable = ttk.StringVar()
        self.settings_compute_variable = ttk.StringVar()
        # self.settings_var5 = ttk.StringVar()
        
        self.settings_frame.columnconfigure((0), weight=1, uniform='a')
        self.settings_frame.columnconfigure((1), weight=2, uniform='a')
        self.settings_frame.rowconfigure((0,1,2,3,4,5,6), weight=1, uniform='a')

        self.settings_frame_label = ttk.Label(self.settings_frame,
                                      text = MAIN_WINDOW['image_processing_settings_label'][app_configuration.locale])
        self.settings_frame_label.grid(row = 0, column = 0, columnspan=2)

        
        

        self.settings_device_label = ttk.Label(self.settings_frame,
                                      text = MAIN_WINDOW["device_label"][app_configuration.locale]) 
        self.settings_device_label.grid(row = 1, column = 0)
        
        self.settings_model_label = ttk.Label(self.settings_frame,
                                              text = MAIN_WINDOW["model_label"][app_configuration.locale])
        self.settings_model_label.grid(row = 2, column = 0)

        self.settings_model_mode_label = ttk.Label(self.settings_frame,
                                                   text = MAIN_WINDOW["mode_label"][app_configuration.locale])
        self.settings_model_mode_label.grid(row = 3, column = 0)

        self.settings_model_mode_label = ttk.Label(self.settings_frame,
                                                   text = MAIN_WINDOW["compute_label"][app_configuration.locale])
        self.settings_model_mode_label.grid(row = 4, column = 0)





        device_list = [f"CPU: {get_processor_name()}"]
        for gpu_id, gpu_name in get_gpus():
            device_list.append(f"{gpu_id}: {gpu_name}")
        
        self.settings_device_list = ttk.Combobox(self.settings_frame, values = device_list, 
                                                 textvariable=self.settings_device_variable, state='readonly')
        self.settings_device_list.set(device_list[0])
        self.settings_device_list.grid(row = 1, column = 1, sticky = 'ew', padx=2)

        # Get the current user's home directory
        self.model_list = installed_models()
        self.settings_model_list = ttk.Combobox(self.settings_frame,
                                                values = self.model_list,
                                                textvariable=self.settings_model_variable,
                                                state='readonly'
                                                )

        self.settings_model_list.set(self.model_list[0])
        self.settings_model_list.grid(row = 2, column = 1, sticky = 'ew', padx=2)
        
        mode_list = ['fast', 'classic', 'best', 'negative']
        self.settings_model_mode_list = ttk.Combobox(self.settings_frame,
                                                     values = mode_list,
                                                     textvariable=self.settings_model_mode_variable,
                                                     state='readonly')
        self.settings_model_mode_list.set(mode_list[0])
        self.settings_model_mode_list.grid(row = 3, column = 1, sticky = 'ew', padx=2)

        compute_list = ['local', 'cloud']
        self.settings_compute_list = ttk.Combobox(self.settings_frame,
                                                     values = compute_list,
                                                     textvariable=self.settings_compute_variable,
                                                     state='readonly')
        self.settings_compute_list.set(compute_list[0])
        self.settings_compute_list.grid(row = 4, column = 1, sticky = 'ew', padx=2)

        



        self.settings_additional_menu_button = ttk.Button(self.settings_frame,
                                                          text = MAIN_WINDOW['additional_settings_button'][app_configuration.locale],
                                                          command = lambda: self.AdditionalSettings(self, self.config_file))
        self.settings_additional_menu_button.grid(row = 6, column = 0, columnspan = 2)


        self.settings_frame.grid(row=0, column=1, sticky='nsew')


        self.process_button = ttk.Button(self,
                                         text = MAIN_WINDOW['process_image_button'][app_configuration.locale],
                                         command = lambda: threading.Thread(target=self.process_image,args=()).start(),
                                         state = 'disabled')
        self.process_button.place(relx = 0.5, 
                                  rely = 0.88, 
                                  anchor = 'center')
        

        self.bind("<Map>", installed_models)


    def recheck(self) -> None:
        self.model_list = installed_models()

    

        
    class AdditionalSettings(ttk.Toplevel):
        def __init__(self, master, config_file):
            super().__init__(master)
            
            self.title(MAIN_WINDOW["additional_settings_title"][app_configuration.locale])
            self.config_file = config_file
            
            # Blip settings
            ttk.Label(self, text="Blip Image Eval Size:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
            self.blip_image_eval_size = ttk.Combobox(self, values=[256, 384, 512], state='readonly')
            self.blip_image_eval_size.grid(row=0, column=1, padx=10, pady=5)
            self.blip_image_eval_size.set(384)
            
            ttk.Label(self, text="Blip Max Length:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
            self.blip_max_length = ttk.Combobox(self, values=[16, 32, 64], state='readonly')
            self.blip_max_length.grid(row=1, column=1, padx=10, pady=5)
            self.blip_max_length.set(config_file.caption_max_length)
            
            ttk.Label(self, text="Blip Offload:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
            self.blip_offload = ttk.Combobox(self, values=[True, False], state='readonly')
            self.blip_offload.grid(row=2, column=1, padx=10, pady=5)
            self.blip_offload.set(config_file.caption_offload)
            
            ttk.Label(self, text="Caption Model Name:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
            self.caption_model_name = ttk.Combobox(self, values=list(CAPTION_MODELS.keys()), state='readonly')
            self.caption_model_name.grid(row=3, column=1, padx=10, pady=5)
            self.caption_model_name.set(config_file.caption_model_name)
            
            # Interrogator settings
            ttk.Label(self, text="Chunk Size:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
            self.chunk_size = ttk.Combobox(self, values=[1024, 2048, 4096], state='readonly')
            self.chunk_size.grid(row=4, column=1, padx=10, pady=5)
            self.chunk_size.set(config_file.chunk_size)
            
            ttk.Label(self, text="Flavor Intermediate Count:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
            self.flavor_intermediate_count = ttk.Combobox(self, values=[1024, 2048, 4096], state='readonly')
            self.flavor_intermediate_count.grid(row=5, column=1, padx=10, pady=5)
            self.flavor_intermediate_count.set(config_file.flavor_intermediate_count)
            
            # Buttons
            self.save_button = ttk.Button(self, text=MAIN_WINDOW["save_settings_button"][app_configuration.locale], command=self.save_settings)
            self.save_button.grid(row=6, column=0, padx=10, pady=10, sticky="w")
            
            self.close_button = ttk.Button(self, text=CLOSE_BUTTON[app_configuration.locale], command=self.destroy)
            self.close_button.grid(row=6, column=1, padx=10, pady=10, sticky="e")
        
        def save_settings(self):
            settings = {
                "blip_max_length": int(self.blip_max_length.get()),
                "blip_offload": bool(self.blip_offload.get()),
                "caption_model_name": self.caption_model_name.get(),
                "chunk_size": int(self.chunk_size.get()),
                "flavor_intermediate_count": int(self.flavor_intermediate_count.get())
            }
            # Implement your saving logic here

            # Update config_file with new settings
            self.config_file.caption_max_length = settings["blip_max_length"]
            self.config_file.caption_offload = settings["blip_offload"]
            self.config_file.caption_model_name = settings["caption_model_name"]
            self.config_file.chunk_size = settings["chunk_size"]
            self.config_file.flavor_intermediate_count = settings["flavor_intermediate_count"]

            self.destroy()
    

    def upload_image(self, *args):
        path = filedialog.askopenfilename()
        if path:
            self.image_file = Image.open(path)
            self.image = ImageTk.PhotoImage(self.image_file)
            self.canvas_for_image.create_image(0, 0, image=self.image, anchor='nw')
            if not self.PICTURE_EXISTS:
                self.upload_button.place_forget()
                self.canvas_for_image.bind('<Button-1>', self.upload_image)
                self.PICTURE_EXISTS = True
            self.canvas_for_image.event_generate("<Configure>", width=self.canvas_for_image.winfo_width(), height=self.canvas_for_image.winfo_height())
            self.process_button['state'] = 'normal'


    def stretch_image(self, event: object) -> None:
        if not self.image:
            return 
        global resized_tk
        width = event.width
        height = event.height

        resized_image = self.image_file.resize((width, height))
        resized_tk = ImageTk.PhotoImage(resized_image)
        self.canvas_for_image.create_image(0, 
                                           0, 
                                           image = resized_tk, 
                                           anchor = 'nw')
    
    def fill_image(self, event: object) -> None:
        if not self.image:
            return
        global resized_tk

        # current ratio
        canvas_ratio = event.width / event.height
        image_ratio = self.image_file.size[0] / self.image_file.size[1]

        if canvas_ratio > image_ratio: # canvas is wider
            width = int(event.width)
            height = int(width / image_ratio)
        else:
            height = int(event.height)
            width = int(height * image_ratio)    

        resized_image = self.image_file.resize((width, height))
        resized_tk = ImageTk.PhotoImage(resized_image)
        self.canvas_for_image.create_image(int(event.width / 2), 
                                           int(event.height / 2),
                                           anchor = 'center',
                                           image = resized_tk)
        



    def process_image(self) -> None:
        self.config_file.clip_model_path = os.path.join(os.path.dirname(__file__), 'models')
        self.process_button['state'] = 'disabled'

        sys.path.insert(0, '..\\clip')
        window = self.ResultsWindow(self)
        from clip_interrogator import Interrogator

        start_time = time.time()
        if self.settings_compute_variable.get() == 'cloud':
            config_req = ""
            for key, elem in self.config_file.__dict__.items():
                if key == "data_path" or key == "device" or key == 'quiet' or key == 'cache_path':
                    continue
                config_req = config_req + f"{key}={elem};"
            request = f"IMG|{os.path.basename(self.image_file.filename)}|{config_req[:-1]}|{self.settings_model_mode_variable.get()}|{USERNAME}"
            client = Client()
            prompts = client.send_image(request, self.image_file.filename)
            if prompts == 'no credit':
                Messagebox.ok(MAIN_WINDOW["no_credits_message"][app_configuration.locale], "No credits!")
            else:
                end_time = time.time()
        else:
            self.config_file.device = "cuda" if self.settings_device_variable.get().split(sep=":")[0][:3] == "GPU" else "cpu"
            self.config_file.download_cache = bool(app_configuration.cache_save)
            ci = Interrogator(self.config_file)
            mode = self.settings_model_mode_variable.get()
            if mode == 'best':
                prompts =  ci.interrogate(self.image_file)
            elif mode == 'classic':
                prompts =  ci.interrogate_classic(self.image_file)
            elif mode == 'fast':
                prompts =  ci.interrogate_fast(self.image_file)
            elif mode == 'negative':
                prompts =  ci.interrogate_negative(self.image_file)
            end_time = time.time()

        window.destroy()
        self.ResultsWindow(self, 
                    self.config_file, 
                    self.settings_model_mode_variable.get(), 
                    self.settings_compute_variable.get(), 
                    self.image_file, 
                    prompts,
                    round((end_time - start_time),3))
        
        self.process_button['state'] = 'enabled'

    class ResultsWindow(ttk.Toplevel):
        def __init__(self, master, config_file=None, mode=None, compute=None, image_file=None, result_prompt=None, computation_time=None):
            super().__init__(master)

            self.title(MAIN_WINDOW["results_title"][app_configuration.locale])
            self.geometry("800x600")
            self.maxsize(900, 600)
            self.minsize(600,400)

            if not config_file:
                threading.Thread(target=self.loader, daemon=True).start()
            else:
                self.window_pack(config_file, mode, compute, image_file, result_prompt, computation_time)
            
        def window_pack(self, config_file, mode, compute, image_file, result_prompt, computation_time) -> None:
            self.image_file = image_file
            self.image = ImageTk.PhotoImage(image_file)
            self.result_prompt = result_prompt

            self.columnconfigure(0, weight=1)
            self.columnconfigure(1, weight=1)
            self.rowconfigure(0, weight=1)

            # Left frame for image
            self.left_frame = ttk.Frame(self)
            self.left_frame.grid(row=0, column=0, sticky='nsew')
            self.left_frame.columnconfigure(0, weight=1)
            self.left_frame.rowconfigure(0, weight=1)

            self.canvas_for_image = Canvas(self.left_frame, borderwidth=0, highlightthickness=0, relief='ridge')
            self.canvas_for_image.grid(row=0, column=0, sticky='nsew')


            # Right frame for settings and prompt
            self.right_frame = ttk.Frame(self)
            self.right_frame.grid(row=0, column=1, sticky='nsew')
            self.right_frame.columnconfigure(0, weight=1)
            self.right_frame.rowconfigure(0, weight=1)
            self.right_frame.rowconfigure(1, weight=3)
            self.right_frame.rowconfigure(2, weight=1)

            # Settings frame
            self.settings_frame = ttk.Frame(self.right_frame)
            self.settings_frame.grid(row=0, column=0, sticky='nsew')
            self.settings_frame.columnconfigure(0, weight=1)

            settings_text = (
                f"{MAIN_WINDOW['device_label'][app_configuration.locale]} {config_file.device}\n"
                f"{MAIN_WINDOW['model_label'][app_configuration.locale]} {config_file.clip_model_name}\n"
                f"{MAIN_WINDOW['mode_label'][app_configuration.locale]} {mode}\n"
                f"{MAIN_WINDOW['compute_label'][app_configuration.locale]} {compute}\n"
                f"{MAIN_WINDOW['computational_time_label'][app_configuration.locale]} {computation_time}s.\n"
            )
            self.settings_label = ttk.Label(self.settings_frame, text=settings_text, justify='left', font=("Helvetica", 20))
            self.settings_label.grid(row=0, column=0, padx=10, pady=10)

            # Prompt frame
            self.prompt_frame = ttk.Frame(self.right_frame)
            self.prompt_frame.grid(row=1, column=0, sticky='nsew')
            self.prompt_frame.columnconfigure(0, weight=1)
            self.prompt_frame.rowconfigure(0, weight=1)

            self.prompt_label = ttk.Label(self.prompt_frame, text=MAIN_WINDOW["results_prompt_label"][app_configuration.locale], justify='left', font=("Helvetica", 18))
            self.prompt_label.grid(row=0, column=0, padx=10, pady=5)

            self.prompt_text = ttk.Text(self.prompt_frame, height=10, wrap='word')
            self.prompt_text.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')
            self.prompt_text.insert('1.0', self.result_prompt)
            self.prompt_text.configure(state='disabled')

            # Buttons frame
            self.buttons_frame = ttk.Frame(self.right_frame)
            self.buttons_frame.grid(row=2, column=0, pady=10)
            self.buttons_frame.columnconfigure([0, 1], weight=1)

            self.copy_button = ttk.Button(self.buttons_frame, text=MAIN_WINDOW["copy_button"][app_configuration.locale], command=self.copy_to_clipboard)
            self.copy_button.grid(row=0, column=0, padx=5)

            self.close_button = ttk.Button(self.buttons_frame, text=CLOSE_BUTTON[app_configuration.locale], command=self.destroy)
            self.close_button.grid(row=0, column=1, padx=5)

            self.resized_tk = None
            self.canvas_for_image.bind('<Configure>', self.stretch_image)
            self.canvas_for_image.bind('<Configure>', self.fill_image)
            self.canvas_for_image.event_generate("<Configure>", width=self.canvas_for_image.winfo_width(), height=self.canvas_for_image.winfo_height())


        def copy_to_clipboard(self):
            pyperclip.copy(self.result_prompt)
        
        def stretch_image(self, event: object) -> None:
            if not self.image:
                return 
            
            width = event.width
            height = event.height

            resized_image = self.image_file.resize((width, height))
            self.resized_tk = ImageTk.PhotoImage(resized_image)
            self.canvas_for_image.create_image(0, 
                                            0, 
                                            image = resized_tk, 
                                            anchor = 'nw')
    
        def loader(self) -> None:
            loading = AnimatedGif(master = self, adjusted_width = self.winfo_width() - 50, adjusted_height= self.winfo_height() - 50)
            loading.pack(expand=True, fill='both')
            text_label = MAIN_WINDOW["image_processing_info_label"][app_configuration.locale]
            image_processing_label = ttk.Label(self, text=text_label, justify='left', font=("Helvetica", 18), anchor='center')
            image_processing_label.pack(expand=True, fill='both')
            while True:
                for i in range(4):
                    new_text = text_label + ("." * i)
                    image_processing_label.configure(text=new_text)
                    time.sleep(0.5)



        def fill_image(self, event: object) -> None:
            if not self.image:
                return

            # current ratio
            canvas_ratio = event.width / event.height
            image_ratio = self.image_file.size[0] / self.image_file.size[1]

            if canvas_ratio > image_ratio: # canvas is wider
                width = int(event.width)
                height = int(width / image_ratio)
            else:
                height = int(event.height)
                width = int(height * image_ratio)    

            resized_image = self.image_file.resize((width, height))
            self.resized_tk = ImageTk.PhotoImage(resized_image)
            self.canvas_for_image.create_image(int(event.width / 2), 
                                            int(event.height / 2),
                                            anchor = 'center',
                                            image = resized_tk)
    



class SettingsTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        # what user can change in settings?
        # Language
        # Theme
        # auto-update option
        # 
        # Click check updates
        # Some info about app
        # 
        # self.write_settings()

        self.current_theme = self.master.master.master.current_theme


        # grid
        self.columnconfigure((0,3), weight=1, uniform='a')
        self.columnconfigure((1,2), weight=4, uniform='a')
        self.rowconfigure((0,1,2,3,4,5), weight=1, uniform='a')

        # info about app

        self.app_name_version = ttk.Label(self,
                                  text = f"{APP_INIT['APP_NAME']}. Version: {APP_INIT['VERSION']}")
        self.app_name_version.grid(row = 0, column = 1, columnspan=2, sticky='nsew')
 
        # language settings
        self.language_setting_frame = ttk.Frame(self)
        self.language_setting_label = ttk.Label(self.language_setting_frame,
                                                text = MAIN_WINDOW["language_label"][app_configuration.locale])
        self.language_setting_variable = ttk.StringVar()
        self.language_list = ["Українська", "English"]
        self.language_setting_combobox = ttk.Combobox(self.language_setting_frame,
                                                      values=["Українська", "English"],
                                                      textvariable=self.language_setting_variable,
                                                      state='readonly')
        self.language_setting_combobox.set(self.language_list[0] if app_configuration.locale == 'UA' else self.language_list[1])
        self.language_setting_label.pack(side='left', fill='both')
        self.language_setting_combobox.pack(side='left', fill='x', padx=5, pady=5)
        self.language_setting_frame.grid(column=1, row=1, sticky='nsew')

        # cmd setting
        self.cmd_display_setting_frame = ttk.Frame(self)
        self.cmd_display_setting_label = ttk.Label(self.cmd_display_setting_frame,
                                                text = MAIN_WINDOW["display_cmd_label"][app_configuration.locale])
        self.cmd_display_setting_variable = ttk.IntVar()
        self.cmd_display_setting_variable.set(app_configuration.cmd)
        self.cmd_display_setting_checkbutton = ttk.Checkbutton(self.cmd_display_setting_frame,
                                                            variable=self.cmd_display_setting_variable,
                                                            )
        self.cmd_display_setting_label.pack(side='left', fill='both')
        self.cmd_display_setting_checkbutton.pack(side='left', fill='x', padx=5, pady=5)
        self.cmd_display_setting_frame.grid(column=2, row=1, sticky='nsew')
        ToolTip(self.cmd_display_setting_frame, text=MAIN_WINDOW["cmd_tooltip"][app_configuration.locale], bootstyle=(INFO, INVERSE))



        # save settings button

        self.save_settings_button = ttk.Button(self,
                                               text = MAIN_WINDOW['save_settings_button'][app_configuration.locale],
                                               command = self.write_settings)
        self.save_settings_button.grid(row = 5, column = 1, sticky='ew', padx=5)


        # check updates button
        self.check_update_button = ttk.Button(self,
                                              text = MAIN_WINDOW["check_updates_button"][app_configuration.locale],
                                              command = self.check_updates)
        self.check_update_button.grid(row = 5, column = 2, sticky='ew', padx=5)


        # change theme button

        self.change_theme_button = ttk.Button(self,
                                              text = MAIN_WINDOW["theme_button"][app_configuration.locale],
                                              command = self.change_current_theme)
        self.change_theme_button.grid(row = 4, column = 2, sticky='ew', padx=5)

        # autoupdate checkbox

        self.autoupdate_check_frame = ttk.Frame(self)
        self.autoupdate_setting_label = ttk.Label(self.autoupdate_check_frame,
                                                text = MAIN_WINDOW["autoupdate_enable_label"][app_configuration.locale])
        self.autoupdate_check_variable = ttk.IntVar()
        self.autoupdate_check_variable.set(app_configuration.auto_update)
        self.autoupdate_setting_checkbutton = ttk.Checkbutton(self.autoupdate_check_frame,
                                                            variable=self.autoupdate_check_variable,
                                                            )
        self.autoupdate_setting_label.pack(side='left', fill='both')
        self.autoupdate_setting_checkbutton.pack(side='left', fill='x', padx=5, pady=5)
        self.autoupdate_check_frame.grid(column=1, row=2, sticky='nsew')
        ToolTip(self.autoupdate_check_frame, text=MAIN_WINDOW["autoupdate_tooltip"][app_configuration.locale], bootstyle=(INFO, INVERSE))

        # save cache model checkbox

        self.cache_model_frame = ttk.Frame(self)
        self.cache_model_label = ttk.Label(self.cache_model_frame,
                                                text = MAIN_WINDOW["save_cache_label"][app_configuration.locale])
        self.cache_model_variable = ttk.IntVar()
        self.cache_model_variable.set(app_configuration.cache_save)
        self.cache_model_checkbutton = ttk.Checkbutton(self.cache_model_frame,
                                                            variable=self.cache_model_variable,
                                                            )
        self.cache_model_label.pack(side='left', fill='both')
        self.cache_model_checkbutton.pack(side='left', fill='x', padx=5, pady=5)
        self.cache_model_frame.grid(column=2, row=2, sticky='nsew')
        ToolTip(self.cache_model_frame, text=MAIN_WINDOW["save_cache_tooltip"][app_configuration.locale], bootstyle=(INFO, INVERSE))
        

    def check_updates(self, silent=True) -> None:
        client = Client() 
        result = client.process_request(f"UPD|{APP_INIT['VERSION']}")
        if result == "True" and not silent:
            Messagebox.ok(MAIN_WINDOW["update_message_newest"][app_configuration.locale], "ImgProPlus Update")
        else:
            mb = Messagebox.yesno(f"{MAIN_WINDOW['update_message_outdated'][app_configuration.locale]}{result}", "ImgProPlus Update")
            if mb == "Yes":
                print("Running update")
                # implement logic here
        

    def change_current_theme(self) -> None:
        if self.current_theme == 'darkly':
            self.current_theme = 'journal'
            self.master.master.master.current_theme = 'journal'
            self.master.master.master.style.theme_use(self.current_theme)
        else:
            self.current_theme = 'darkly'
            self.master.master.master.current_theme = 'darkly'
            self.master.master.master.style.theme_use(self.current_theme)


    def write_settings(self) -> None:
        settings_dictionary = {"locale" : "EN" if self.language_setting_variable.get() == "English" else "UA",
                               "cmd" : self.cmd_display_setting_variable.get(),
                               "theme" : self.master.master.master.current_theme,
                               "auto_update" : self.autoupdate_check_variable.get(),
                               "cache_model" : self.cache_model_variable.get()
                               }

        file_path = os.path.dirname(os.path.realpath(__file__)) + "\\configs\\user_settings"
        with open(file_path, "w") as file:
            for key, element in settings_dictionary.items():
                file.write(f"{key}:{element}\n")
        
        messagebox_answer = Messagebox.yesno(f"{MAIN_WINDOW['message_restart_app_settings'][app_configuration.locale]}", MAIN_WINDOW['message_title_restart_app_settings'][app_configuration.locale])
        if messagebox_answer:
            self.master.master.master.restart_app()
        

class DocumentationTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.docs_uploaded = False
        #self.frame = tkinterweb.HtmlFrame(self, messages_enabled=False)
        self.bind("<Configure>", self.on_frame_pack)



    def on_frame_pack(self, event):
        if self.pack_info() is not None and not self.docs_uploaded:
            try:
                self.frame = tkinterweb.HtmlFrame(self, messages_enabled=False)
                if app_configuration.locale == 'EN':
                    self.frame.load_file(os.path.join(os.path.dirname(__file__), 'docs.html'))
                else:
                    self.frame.load_file(os.path.join(os.path.dirname(__file__), 'docs_u.html'))
                self.frame.pack(expand=True, fill='both')
                self.docks_uploaded = True
            except FileNotFoundError as e:
                logger.error("Not found documentation file")

    def test(self):

        self.frame = tkinterweb.HtmlFrame(self, messages_enabled=False)
        try:
            if app_configuration.locale == 'EN':
                self.frame.load_file(os.path.join(os.path.dirname(__file__), 'docs.html'))
            else:
                self.frame.load_file(os.path.join(os.path.dirname(__file__), 'docs_u.html'))
            self.frame.pack(expand=True, fill='both')
            self.docks_uploaded = True
        except FileNotFoundError as e:
            logger.error("Not found documentation file")


        


class SendQuestionTab(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        # self.style = Style(theme="yeti")  # Change the theme as needed

        self.columnconfigure(1, weight=6, uniform='a')
        self.columnconfigure((0,2), weight=1, uniform='a')
        self.rowconfigure(0, weight=5, uniform='a')
        self.rowconfigure(1, weight=3, uniform='a')

        self.create_widgets()

    def create_widgets(self):
        # Create text field
        self.text_field = ScrolledText(self, padding=5, height=10, autohide=True)  # Adjust width
        self.text_field.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')  # Adjust padx and pady

        # Create send button
        self.send_button = ttk.Button(self, text=MAIN_WINDOW["send_q_button"][app_configuration.locale], command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=150, pady=(0, 10), sticky="ew") 

    def send_message(self):
        client = Client()
        message = client.process_request(f'MSG|{self.text_field.get("1.0", ttk.END)}|{USERNAME}')
        if message == "True":
            Messagebox.ok(MAIN_WINDOW["message_sent"][app_configuration.locale], MAIN_WINDOW["message_sent_title"][app_configuration.locale])
            self.text_field.delete(1.0, ttk.END)
        else:
            Messagebox.show_error(MAIN_WINDOW["message_sent_error"][app_configuration.loclae], "Something went wrong!")
    
        

class ExtensionsTab(ttk.Frame):
    def __init__(self, master: ttk.Frame):
        super().__init__(master=master)
        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True)

        # Treeview frame on the left
        tree_frame = ttk.Frame(main_frame, width=200)
        tree_frame.pack(side='left', fill='y')
        
        label = ttk.Label(tree_frame, text=MAIN_WINDOW["models_label"][app_configuration.locale], font=("Helvetica", 14, "bold"))
        label.pack(side='top', pady=6)
        
        self.tree = ttk.Treeview(tree_frame)
        self.tree.pack(fill='both', expand=True, padx=3)

        text_frame = ttk.Frame(main_frame)
        text_frame.pack(side='right', fill='both', expand=True)
        
        self.button_frame = ttk.Frame(text_frame)
        self.button_frame.pack(side='top', fill='x')
        
        self.button = ttk.Button(self.button_frame, text=MAIN_WINDOW["download_button"][app_configuration.locale],state='disabled')
        self.button.pack(side='right', padx=5, pady=5)
        
        # Text frame on the right

        
        self.text = ttk.Text(text_frame, wrap='word', state='disabled')
        self.text.pack(fill='both', expand=True)
        
        # Button frame at the bottom of the text frame

        
        # Adding some sample elements
        self.elements = {}
        self.get_models()
        
        for element in self.elements:
            self.tree.insert('', 'end', text=element, tags=())
        
        # Bind the treeview selection
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def on_tree_select(self, event):
        self.selected_item = self.tree.selection()[0]
        self.element_name = self.tree.item(self.selected_item, 'text')
        description = self.elements.get(self.element_name, MAIN_WINDOW["description_unavailable_label"][app_configuration.locale])
        self.text.configure({"state": "normal"})
        self.text.delete(1.0, ttk.END)
        self.text.insert(ttk.END, description[0])
        self.text.configure({"state": "disabled"})

        models = installed_models()
        filtered_element = self.element_name.replace("/", "_").replace("-", "_").replace('.', "_").lower()
        if description[1] == "1" and subscription_status_verification() == "No":
            self.button.configure(text = MAIN_WINDOW["buy_premium_button"][app_configuration.locale],
                                  command = self.attempt_without_premium,
                                  bootstyle = "warning",
                                  state='enabled')
        elif filtered_element in [model.replace("/", "_").replace("-", "_").replace('.', "_").lower() for model in models]:
            self.button.configure(text = MAIN_WINDOW["installed_label"][app_configuration.locale], state='disabled')
        else:
            self.button.configure(text = MAIN_WINDOW["download_button"][app_configuration.locale],
                                  command = lambda: threading.Thread(target = self.download_model, args=(self.element_name,)).start(),
                                  state = 'enabled',
                                  bootstyle='default')




    def attempt_without_premium(self):
        user_answer = Messagebox.okcancel(MAIN_WINDOW["proposition_message"][app_configuration.locale], MAIN_WINDOW["proposition_title"][app_configuration.locale])
        if user_answer:
            PaymentWindow(self, serv_conn=True)

    def get_models(self):
        client = Client()
        results = client.process_request(f"EXT")
        if results == "Error":
            Messagebox.show_error(MAIN_WINDOW["error_model_download"][app_configuration.locale], MAIN_WINDOW["error_model_download_title"][app_configuration.locale])
        models = results.split(sep="|")
        for model in models:
            temp = model.split(sep=";")
            self.elements[temp[0]] = [temp[1], temp[2]]
        #print(self.master.frames[MAIN_WINDOW['notebook_mainpage_tab'][app_configuration.locale]])

    # def download_model_with_progress(self, model_name, result):
    #     with redirect_stdout():
    #         process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
            
    #         # Initialize the progress bar
    #         for line in process.stdout:
    #                 # Parse the progress from each line of output
    #             progress = parse_progress(line)
    #             if not progress:
    #                 continue
    #             self.progress_var.set(int(progress))
    #             # Update the progress bar
            
    #         process.wait()
            
        

        # def parse_progress(line):
        #     try:
        #         if "%" in line:
        #             progress = int(line.split('%')[0].split()[-1])  # Adjust based on your command's output
        #             print(progress)
        #             return progress
        #     except Exception as e:
        #         return None
        #     return None

    
    def download_model(self, model_name):
        
        from clip_interrogator import download_model_gui
        try:
            self.button.pack_forget()
            self.progress_var = ttk.IntVar()
            self.progress = ttk.Progressbar(
                master = self.button_frame,
                length = 100,
                maximum = 100,
                mode = 'indeterminate',
                variable = self.progress_var,
                bootstyle = 'success-striped'
            )
            self.progress.pack(fill='both', expand=True, padx=20, pady=13)
            self.progress.start()
            result = []
            model_thread = threading.Thread(target = download_model_gui, args=(model_name, result))
            model_thread.start()
            self.button.configure(bootstyle = 'success-outline')
            while model_thread.is_alive():
                for i in range(0,4):
                    self.button.configure(text = f"{MAIN_WINDOW['downloading_model'][app_configuration.locale]}{i*'.'}")
                    time.sleep(1)
            if result[0]:
                self.progress.pack_forget()
                self.button.pack(side='right', padx=5, pady=5)
                self.button.configure(text = MAIN_WINDOW["installed_label"][app_configuration.locale], state='disabled')
                self.get_models()
                self.master.update_idletasks()
        except Exception as e:
            logger.error(f"Error with model downloading. {e}")



class PaymentWindow(ttk.Toplevel):
    def __init__(self, master, serv_conn=False):
        super().__init__(master)

        self.title(MAIN_WINDOW["payment_window_title"][app_configuration.locale])
        self.geometry('900x700')
        self.minsize(600, 700)
        self.maxsize(1000, 700)
        self.resizable(True, True)
        self.promotion_frames = []

        if serv_conn:
            client = Client()
            self.data = client.process_request(f"SUB|{app_configuration.locale}")
            self.display_promotions()
        else:
            self.data = None

        


        # Add close button at the bottom
        self.close_button = ttk.Button(self, text=CLOSE_BUTTON[app_configuration.locale], command=self.destroy)
        self.close_button.pack(side="bottom", pady=10)

    def display_promotions(self):
        promotions = self.data.split('|')
        
        for promotion in promotions:
            promotion_data = promotion.split(';')
            description = promotion_data[0]
            price = promotion_data[1]
            details = promotion_data[2]

            # Create a frame for each promotion
            promotion_frame = ttk.Frame(self, padding="10")
            promotion_frame.pack(fill='both', pady=10, padx=10, expand=True)
            self.promotion_frames.append(promotion_frame)

            # Add description label
            description_label = ttk.Label(promotion_frame, text=description, font=("Helvetica", 16, "bold"))
            description_label.pack(anchor='w')

            # Add details label
            details_label = ttk.Label(promotion_frame, text=details, font=("Helvetica", 12))
            details_label.pack(anchor='w')

            # Add price label
            price_label = ttk.Label(promotion_frame, text=f"{MAIN_WINDOW['price_label'][app_configuration.locale]} ${price}", font=("Helvetica", 12, "italic"))
            price_label.pack(anchor='w')

            # Add a pay button
            button = ttk.Button(promotion_frame, text=MAIN_WINDOW["pay_button"][app_configuration.locale], command=lambda d=description, p=price: self.make_payment(d, p))
            button.pack(anchor='e', pady=5)

    def make_payment(self, description, price):
        # Clear all promotion frames
        for frame in self.promotion_frames:
            frame.pack_forget()

        # Form QR code and output it in the window

        html_code = """<form method="post" action="https://www.liqpay.ua/api/3/checkout/" accept-charset="utf-8">
    <input type='hidden' name='data' value='eyJhY3Rpb24iOiAicGF5IiwgImFtb3VudCI6ICIxIiwgImN1cnJlbmN5IjogIlVTRCIsICJkZXNjcmlwdGlvbiI6ICJkZXNjcmlwdGlvbiB0ZXh0IiwgIm9yZGVyX2lkIjogIm9yZGVyX2lkXzEiLCAidmVyc2lvbiI6ICIzIiwgInB1YmxpY19rZXkiOiAiVnpReDhIdDYkSlkjOUBXeTJMcyZrY1RHN25QWDVScSpCVTBGajMhZE0xYU9aTklENFFydiVFYmhmK0NwIiwgImxhbmd1YWdlIjogInJ1IiwgInNhbmRib3giOiAwfQ=='>
    <input type='hidden' name='signature' value='mR6C9v45XLgNrVNg4UeqvEA820E='>
    <input type="image" src="//static.liqpay.ua/buttons/p1ru.radius.png" name="btn_text">
    </form>"""
        
        url = "http://www.liqpay.ua/checkout?action=pay?currency=USD?version=3?amount=" + price + "?description=" + description
        self.create_qr_code(url, description, price)



        # Add "Back" button to return to promotions
        self.back_button = ttk.Button(self, text=MAIN_WINDOW["back_button"][app_configuration.locale], command=self.back_to_promotions)
        self.back_button.pack(pady=10)

        # Hide the close button
        self.close_button.pack_forget()

    def back_to_promotions(self):
        # Remove QR code and instruction label
        self.qr_label.pack_forget()
        self.instruction_label.pack_forget()
        self.payment_info_label.pack_forget()
        self.back_button.pack_forget()
        self.direct_link_label.pack_forget()

        # Show promotion frames again
        for frame in self.promotion_frames:
            frame.pack(fill='both', pady=10, padx=10, expand=True)

        # Show the close button again
        self.close_button.pack(side="bottom", pady=10)

    def create_qr_code(self, url, description, price):
        img = qrcode.make(url, image_factory=qrcode.image.pil.PilImage)

        qr_photo = ImageTk.PhotoImage(img.get_image())

        self.qr_label = ttk.Label(self, image=qr_photo)
        self.qr_label.image = qr_photo  # keep a reference to prevent garbage collection
        self.qr_label.pack()

        import webbrowser
        # Add direct link label
        self.direct_link_button = ttk.Button(self, text=MAIN_WINDOW['direct_link'][app_configuration.locale], command = lambda: webbrowser.open_new(url))
        self.direct_link_button.pack(pady=5)
               

        self.payment_info_label = ttk.Label(self, text=f"{description}\n${price}")
        self.payment_info_label.pack(pady=10)
        
        
        self.instruction_label = ttk.Label(self, text=MAIN_WINDOW["scan_code_tip"][app_configuration.locale])
        self.instruction_label.pack(pady=10)

    def respond_to_user(self) -> None:
        #!/bin/bash
        # PUBLIC_KEY='your_public_key'
        # PRIVATE_KEY='your_private_key'
        # API_URL='https://www.liqpay.ua/api/request'
        # JSON="{ 
        # \"action\" : \"ticket\",
        #     \"version\" : 3,
        #     \"public_key\" : \"${PUBLIC_KEY}\", 
        #     \"order_id\" : \"order_id_1\",
        #     \"email\" : \"email@gmail.com\"
        # }"
        # # DATA is base64_encode result from JSON string
        # DATA=$(echo -n ${JSON} | base64)
        # # SIGNATURE is base64 encode result from sha1 binary hash from concatenate string ${PRIVATE_KEY}${DATA}${PRIVATE_KEY}
        # SIGNATURE=$(echo -n "${PRIVATE_KEY}${DATA}${PRIVATE_KEY}" | openssl dgst -binary -sha1 | base64)
        # # REQ is json response from liqpay
        # REQ=$(curl --silent -XPOST ${API_URL} --data-urlencode data="${DATA}" --data-urlencode signature="${SIGNATURE}")
        # echo "Result: ${REQ}"
        pass


class AnimatedGif(ttk.Frame):
    def __init__(self, master, adjusted_width, adjusted_height):
        super().__init__(master, width=adjusted_width, height=adjusted_height)

        # open the GIF and create a cycle iterator
        file_path = os.path.join(os.path.dirname(__file__), "loading.gif")
        with Image.open(file_path) as im:
            # create a sequence
            sequence = ImageSequence.Iterator(im)
            images = [ImageTk.PhotoImage(s) for s in sequence]
            self.image_cycle = cycle(images)

            # length of each frame
            self.framerate = im.info["duration"]

        self.img_container = ttk.Label(self, image=next(self.image_cycle), anchor='center')
        self.img_container.pack(fill="both", expand=True)
        self.after(self.framerate, self.next_frame)

    def next_frame(self):
        """Update the image for each frame"""
        self.img_container.configure(image=next(self.image_cycle))
        self.after(self.framerate, self.next_frame)


def installed_models(*args) -> list [str]:
    # Construct the path to the desired directory
    cache_clip_path = os.path.dirname(os.path.realpath(__file__)) + "\\models"
    models = []
    if os.path.exists(cache_clip_path):
        elements = os.listdir(cache_clip_path)
        for element in elements:
            if element[:6] == "models":
                models.append(element.split(sep="CLIP-")[1])
            elif element.split(sep=".")[1] == 'pt':
                models.append(element.split(sep=".")[0])
        return models
    else:
        return []

def subscription_status_verification() -> str:
    client = Client()
    result = client.process_request(f"SSV|{USERNAME}")
    if result != "False":
        return result
    else: return "No"


if __name__ == '__main__':
    print("nothing")
    root = ttk.Window()
    PaymentWindow(root)
    root.mainloop()
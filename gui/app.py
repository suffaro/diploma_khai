from settings import ApplicationConfiguration, APP_INIT
from localization import MAIN_WINDOW
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
from clip_interrogator import Config, CAPTION_MODELS
import threading
from pathlib import Path
from itertools import cycle
import time
import pyperclip

app_configuration = ApplicationConfiguration()

class MainPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master = master)

        self.app_configuration = ApplicationConfiguration()


        self.current_theme = master.current_theme
        #self.style.theme_use(self.current_theme)

        # Create a custom style for the tabs

        customed_style = ttk.Style()
        customed_style.configure('Custom.TNotebook.Tab', padding=[12, 12], font=('Helvetica', 10),)
        customed_style.configure('Custom.TNotebook', tabmargins = (20,20,20,20))
        notebook = ttk.Notebook(master = self)

        tab1 = MainTab(notebook)
        tab2 = ExtensionsTab(notebook)
        #tab3 = SendQuestionTab(notebook)
        tab3 = ttk.Frame(notebook)
        tab4 = ttk.Frame(notebook)
        tab5 = SettingsTab(notebook)
        tab6 = AccountTab(notebook)

        extensions = [("Extension1", "Description1"), ("Extension2", "Description2")]
        for extension, description in extensions:
            tab2.treeview.insert("", "end", text=extension, values=(description,))

        notebook.add(tab1, text=MAIN_WINDOW['notebook_mainpage_tab'][app_configuration.locale])
        notebook.add(tab2, text=MAIN_WINDOW['notebook_extensions_tab'][app_configuration.locale])
        notebook.add(tab3, text=MAIN_WINDOW['notebook_qa_tab'][app_configuration.locale])
        notebook.add(tab4, text=MAIN_WINDOW['notebook_docs_tab'][app_configuration.locale])
        notebook.add(tab5, text=MAIN_WINDOW['notebook_settings_tab'][app_configuration.locale])
        notebook.add(tab6, text=MAIN_WINDOW['notebook_account_tab'][app_configuration.locale])

        notebook.pack(expand = True, fill = 'both', )

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

        self.username = os.getenv("IMG_PLUS").split(sep="|")[0]

        self.username_label_name = ttk.Label(self,
                                             text = "Username:")
        self.username_label_name.grid(column=1, row=0, sticky='nsew')


        self.username_label = ttk.Label(self,
                                        text = self.username)
        self.username_label.grid(column=2, row=0, sticky='nsew')

        # subscription
        self.subscription_status_label = ttk.Label(self,
                                                   text = MAIN_WINDOW["subscription_label"][app_configuration.locale])
        self.subscription_status_label.grid(column=1, row=1, sticky='nsew')

        self.subscription_status_variable = self.subscription_status_verification(self.username)
        self.subscription_status = ttk.Label(self)
        if self.subscription_status_variable == "No":
            self.subscription_status['text'] = "No"
        else:
            self.subscription_status['text'] = f"Yes (up to {self.subscription_status_variable})"
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
                                        command= lambda: PaymentWindow(self.master))
        self.purchase_subscription_button.grid(row = 3, column = 2, sticky='ew', padx=4)




    def logout(self) -> None:
        # os.system("REG delete HKCU\Environment /F /V IMG_PLUS")
        self.master.master.master.destroy()


    def subscription_status_verification(self, username) -> str:
        client = Client()
        result = client.process_request(f"SSV|{username}")
        if result != "False":
            return result
        else: return "No"

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
                                      text = "Device:") 
        self.settings_device_label.grid(row = 1, column = 0)
        
        self.settings_model_label = ttk.Label(self.settings_frame,
                                              text = "Model:")
        self.settings_model_label.grid(row = 2, column = 0)

        self.settings_model_mode_label = ttk.Label(self.settings_frame,
                                                   text = "Mode:")
        self.settings_model_mode_label.grid(row = 3, column = 0)

        self.settings_model_mode_label = ttk.Label(self.settings_frame,
                                                   text = "Compute:")
        self.settings_model_mode_label.grid(row = 4, column = 0)





        device_list = [f"CPU: {get_processor_name()}"]
        for gpu_id, gpu_name in get_gpus():
            device_list.append(f"{gpu_id}: {gpu_name}")
        
        self.settings_device_list = ttk.Combobox(self.settings_frame, values = device_list, textvariable=self.settings_device_variable)
        self.settings_device_list.set(device_list[0])
        self.settings_device_list.grid(row = 1, column = 1, sticky = 'ew', padx=2)

        # Get the current user's home directory
        model_list = self.installed_models()
        self.settings_model_list = ttk.Combobox(self.settings_frame,
                                                values = model_list,
                                                textvariable=self.settings_model_variable
                                                )
        self.settings_model_list.set(model_list[0])
        self.settings_model_list.grid(row = 2, column = 1, sticky = 'ew', padx=2)
        
        mode_list = ['fast', 'classic', 'best', 'negative']
        self.settings_model_mode_list = ttk.Combobox(self.settings_frame,
                                                     values = mode_list,
                                                     textvariable=self.settings_model_mode_variable)
        self.settings_model_mode_list.set(mode_list[0])
        self.settings_model_mode_list.grid(row = 3, column = 1, sticky = 'ew', padx=2)

        compute_list = ['local', 'cloud']
        self.settings_compute_list = ttk.Combobox(self.settings_frame,
                                                     values = compute_list,
                                                     textvariable=self.settings_compute_variable)
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
        
    def installed_models(self) -> list:
        home_dir = os.path.expanduser("~")
        # Construct the path to the desired directory
        cache_clip_path = os.path.join(home_dir, ".cache", "clip")
        if os.path.exists(cache_clip_path):
            print("Directory found at:", cache_clip_path)
            elements = [elem.split(sep='.')[0] for elem in os.listdir(cache_clip_path) if elem.split(sep='.')[1] == 'pt']
            print(elements)
            return elements
        else:
            print("Directory not found.")
            return []
    
    def start_image_processing(self):
        process_thread = threading.Thread(target = self.process_image, args=())


        
    class AdditionalSettings(ttk.Toplevel):
        def __init__(self, master, config_file):
            super().__init__(master)
            
            self.title("Settings")
            self.config_file = config_file
            
            # Blip settings
            ttk.Label(self, text="Blip Image Eval Size:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
            self.blip_image_eval_size = ttk.Combobox(self, values=[256, 384, 512])
            self.blip_image_eval_size.grid(row=0, column=1, padx=10, pady=5)
            self.blip_image_eval_size.set(384)
            
            ttk.Label(self, text="Blip Max Length:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
            self.blip_max_length = ttk.Combobox(self, values=[16, 32, 64])
            self.blip_max_length.grid(row=1, column=1, padx=10, pady=5)
            self.blip_max_length.set(config_file.caption_max_length)
            
            ttk.Label(self, text="Blip Offload:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
            self.blip_offload = ttk.Combobox(self, values=[True, False])
            self.blip_offload.grid(row=2, column=1, padx=10, pady=5)
            self.blip_offload.set(config_file.caption_offload)
            
            ttk.Label(self, text="Caption Model Name:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
            self.caption_model_name = ttk.Combobox(self, values=list(CAPTION_MODELS.keys()))
            self.caption_model_name.grid(row=3, column=1, padx=10, pady=5)
            self.caption_model_name.set(config_file.caption_model_name)
            
            # Interrogator settings
            ttk.Label(self, text="Chunk Size:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
            self.chunk_size = ttk.Combobox(self, values=[1024, 2048, 4096])
            self.chunk_size.grid(row=4, column=1, padx=10, pady=5)
            self.chunk_size.set(config_file.chunk_size)
            
            ttk.Label(self, text="Flavor Intermediate Count:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
            self.flavor_intermediate_count = ttk.Combobox(self, values=[1024, 2048, 4096])
            self.flavor_intermediate_count.grid(row=5, column=1, padx=10, pady=5)
            self.flavor_intermediate_count.set(config_file.flavor_intermediate_count)
            
            # Buttons
            self.save_button = ttk.Button(self, text="Save Settings", command=self.save_settings)
            self.save_button.grid(row=6, column=0, padx=10, pady=10, sticky="w")
            
            self.close_button = ttk.Button(self, text="Close", command=self.destroy)
            self.close_button.grid(row=6, column=1, padx=10, pady=10, sticky="e")
        
        def save_settings(self):
            settings = {
                "blip_max_length": int(self.blip_max_length.get()),
                "blip_offload": bool(self.blip_offload.get()),
                "caption_model_name": self.caption_model_name.get(),
                "chunk_size": int(self.chunk_size.get()),
                "flavor_intermediate_count": int(self.flavor_intermediate_count.get())
            }
            print("Settings saved:", settings)
            # Implement your saving logic here

            # Update config_file with new settings
            self.config_file.caption_max_length = settings["blip_max_length"]
            self.config_file.caption_offload = settings["blip_offload"]
            self.config_file.caption_model_name = settings["caption_model_name"]
            self.config_file.chunk_size = settings["chunk_size"]
            self.config_file.flavor_intermediate_count = settings["flavor_intermediate_count"]
            
            print(self.config_file)

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
        loader = AnimatedGif(self)
        loader.grid(column=0, row=0, sticky='nsew')
        self.process_button['state'] = 'disabled'

        start_time = time.time()
        if self.settings_compute_variable.get() == 'cloud':
            config_req = ""
            for key, elem in self.config_file.__dict__.items():
                if key == "data_path" or key == "device" or key == 'quiet' or key == 'cache_path':
                    continue
                config_req = config_req + f"{key}={elem};"
            request = f"IMG|{os.path.basename(self.image_file.filename)}|{config_req[:-1]}|{self.settings_model_mode_variable.get()}|{os.getenv('IMG_PLUS').split(sep='|')[0]}"
            print(request)
            client = Client()
            prompts = client.send_image(request, self.image_file.filename)
            if prompts == 'no credit':
                Messagebox.ok("You don't have credits left :(", "No credits!")
            else:
                print(prompts)
                end_time = time.time()
        else:
            from clip_interrogator import Interrogator
            self.config_file.clip_model_name = 'ViT-H-14/laion2b_s32b_b79k'
            self.config_file.device = "cuda" if self.settings_device_variable.get().split(sep=":")[0][:3] == "GPU" else "cpu"
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
            print(prompts)
            end_time = time.time()
            print("done interrogati")
        self.ResultsWindow(self, 
                    self.config_file, 
                    self.settings_model_mode_variable.get(), 
                    self.settings_compute_variable.get(), 
                    self.image_file, 
                    prompts,
                    round((end_time - start_time),3))
        
        self.process_button['state'] = 'enabled'
        loader.grid_forget()

    class ResultsWindow(ttk.Toplevel):
        def __init__(self, master, config_file, mode, compute, image_file, result_prompt, computation_time):
            super().__init__(master)

            self.title("Results")
            self.geometry("800x600")
            self.maxsize(1200, 900)
            self.minsize(600,400)

            self.image_file = image_file
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
                f"Device: {config_file.device}\n"
                f"Model: {config_file.clip_model_name}\n"
                f"Mode: {mode}\n"
                f"Compute: {compute}\n"
                f"Computation time: {computation_time}s.\n"
            )
            self.settings_label = ttk.Label(self.settings_frame, text=settings_text, justify='left')
            self.settings_label.grid(row=0, column=0, padx=10, pady=10)

            # Prompt frame
            self.prompt_frame = ttk.Frame(self.right_frame)
            self.prompt_frame.grid(row=1, column=0, sticky='nsew')
            self.prompt_frame.columnconfigure(0, weight=1)
            self.prompt_frame.rowconfigure(0, weight=1)

            self.prompt_label = ttk.Label(self.prompt_frame, text="Resulting Prompt:", justify='left')
            self.prompt_label.grid(row=0, column=0, padx=10, pady=5)

            self.prompt_text = ttk.Text(self.prompt_frame, height=10, wrap='word')
            self.prompt_text.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')
            self.prompt_text.insert('1.0', self.result_prompt)
            self.prompt_text.configure(state='disabled')

            # Buttons frame
            self.buttons_frame = ttk.Frame(self.right_frame)
            self.buttons_frame.grid(row=2, column=0, pady=10)
            self.buttons_frame.columnconfigure([0, 1], weight=1)

            self.copy_button = ttk.Button(self.buttons_frame, text="Copy", command=self.copy_to_clipboard)
            self.copy_button.grid(row=0, column=0, padx=5)

            self.close_button = ttk.Button(self.buttons_frame, text="Close", command=self.destroy)
            self.close_button.grid(row=0, column=1, padx=5)

            self.resized_tk = None
            self.canvas_for_image.bind('<Configure>', self.stretch_image)
            self.canvas_for_image.bind('<Configure>', self.fill_image)

        def copy_to_clipboard(self):
            pyperclip.copy(self.result_prompt)
        
        def stretch_image(self, event: object) -> None:
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

        self.current_theme = self.master.master.current_theme


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
                                                text = "Language:")
        self.language_setting_variable = ttk.StringVar()
        self.language_list = ["Українська", "English"]
        self.language_setting_combobox = ttk.Combobox(self.language_setting_frame,
                                                      values=["Українська", "English"],
                                                      textvariable=self.language_setting_variable)
        self.language_setting_combobox.set(self.language_list[0] if app_configuration.locale == 'UA' else self.language_list[1])
        self.language_setting_label.pack(side='left', fill='both')
        self.language_setting_combobox.pack(side='left', fill='x', padx=5, pady=5)
        self.language_setting_frame.grid(column=1, row=1, sticky='nsew')

        # cmd setting
        self.cmd_display_setting_frame = ttk.Frame(self)
        self.cmd_display_setting_label = ttk.Label(self.cmd_display_setting_frame,
                                                text = "Display CMD:")
        self.cmd_display_setting_variable = ttk.IntVar()
        self.cmd_display_setting_variable.set(app_configuration.cmd)
        self.cmd_display_setting_checkbutton = ttk.Checkbutton(self.cmd_display_setting_frame,
                                                            variable=self.cmd_display_setting_variable,
                                                            )
        self.cmd_display_setting_label.pack(side='left', fill='both')
        self.cmd_display_setting_checkbutton.pack(side='left', fill='x', padx=5, pady=5)
        self.cmd_display_setting_frame.grid(column=2, row=1, sticky='nsew')
        ToolTip(self.cmd_display_setting_frame, text="When enabled, shows you CMD with progress", bootstyle=(INFO, INVERSE))



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
                                                text = "Autoupdate enabled:")
        self.autoupdate_check_variable = ttk.IntVar()
        self.autoupdate_check_variable.set(app_configuration.auto_update)
        self.autoupdate_setting_checkbutton = ttk.Checkbutton(self.autoupdate_check_frame,
                                                            variable=self.autoupdate_check_variable,
                                                            )
        self.autoupdate_setting_label.pack(side='left', fill='both')
        self.autoupdate_setting_checkbutton.pack(side='left', fill='x', padx=5, pady=5)
        self.autoupdate_check_frame.grid(column=1, row=2, sticky='nsew')
        ToolTip(self.autoupdate_check_frame, text="When enabled, checks for updates when app starts", bootstyle=(INFO, INVERSE))

        # save cache model checkbox

        self.cache_model_frame = ttk.Frame(self)
        self.cache_model_label = ttk.Label(self.cache_model_frame,
                                                text = "Save cache files:")
        self.cache_model_variable = ttk.IntVar()
        self.cache_model_variable.set(app_configuration.cache_save)
        self.cache_model_checkbutton = ttk.Checkbutton(self.cache_model_frame,
                                                            variable=self.cache_model_variable,
                                                            )
        self.cache_model_label.pack(side='left', fill='both')
        self.cache_model_checkbutton.pack(side='left', fill='x', padx=5, pady=5)
        self.cache_model_frame.grid(column=2, row=2, sticky='nsew')
        ToolTip(self.cache_model_frame, text="When enabled, increases performance of model on your machine, by saving safetensor files. Read more about it in Docs.", bootstyle=(INFO, INVERSE))
        

    def check_updates(self, silent=True) -> None:
        client = Client() 
        result = client.process_request(f"UPD|{APP_INIT['VERSION']}")
        if result == "True" and not silent:
            Messagebox.ok("ImgProPlus Update", "Your application is up to date.")
        else:
            mb = Messagebox.yesno(f"Your application is out dated. New version available - {result}", "ImgProPlus Update")
            if mb == "Yes":
                print("Running update")
        

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

        file_path = os.path.dirname(os.path.realpath(__file__)) + "\\user_settings"
        with open(file_path, "w") as file:
            for key, element in settings_dictionary.items():
                file.write(f"{key}:{element}\n")

class DocumentationTab(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)   


class SendQuestionTab(ttk.Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        # self.style = Style(theme="yeti")  # Change the theme as needed

        self.columnconfigure(1, weight=3, uniform='a')
        self.columnconfigure((0,2), weight=1, uniform='a')
        self.rowconfigure((0,1,2,3,4), weight=1, uniform='a')
        self.create_widgets()

    def create_widgets(self):
        # Create text field
        self.text_field = ScrolledText(self, padding=5, height=10, autohide=True)  # Adjust width
        self.text_field.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')  # Adjust padx and pady

        # Create send button
        self.send_button = ttk.Button(self, text="Send", command=self.send_message)
        self.send_button.grid(row=5, column=1, padx=10, pady=(0, 10), sticky="nsew") 

    def send_message(self):
        message = True
        if message:
            Messagebox.ok("Message Sent", "Message sent successfully!")
            self.text_field = ScrolledText(self, padding=5, height=10, autohide=True)
    
        

class ExtensionsTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.style = ttk.Style()
        self.style.configure("Treeview", font=("Helvetica", 12))

        # Create a treeview widget for the left part (menu)
        self.treeview = ttk.Treeview(self, columns=("Description"))
        self.treeview.heading("#0", text="Extension")
        self.treeview.heading("Description", text="Description")
        self.treeview.pack(side="left", fill="y", expand=True)

        # Create a frame for the right part
        self.info_frame = ttk.Frame(self)
        self.info_frame.pack(side="left", fill="both", expand=True)

        # Create labels or text widgets to display information about the selected extension
        self.extension_label = ttk.Label(self.info_frame, text="Selected Extension:")
        self.extension_label.pack()

        self.description_label = ttk.Label(self.info_frame, text="Description:")
        self.description_label.pack()

        # Bind the treeview widget to a function to update the information displayed in the right part
        self.treeview.bind("<<TreeviewSelect>>", self.on_select)

    def on_select(self, event):
        # Retrieve the selected item from the treeview
        selected_item = self.treeview.selection()
        if selected_item:
            item_text = self.treeview.item(selected_item)["text"]
            item_description = self.treeview.item(selected_item)["values"][0]

            # Update the labels or text widgets with the selected item's information
            self.extension_label.config(text=f"Selected Extension: {item_text}")
            self.description_label.config(text=f"Description: {item_description}")


class PaymentWindow(ttk.Toplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Payment Window")
        self.geometry = ('900x700')
        self.minsize(600,600)
        self.maxsize(1000,600)
        self.resizable(True, True)

        self.mainloop()

class AnimatedGif(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, width=400, height=300)

        # open the GIF and create a cycle iterator
        file_path = Path(__file__).parent.parent / "giphy_2.gif"
        with Image.open(file_path) as im:
            # create a sequence
            sequence = ImageSequence.Iterator(im)
            images = [ImageTk.PhotoImage(s) for s in sequence]
            self.image_cycle = cycle(images)

            # length of each frame
            self.framerate = im.info["duration"]

        self.img_container = ttk.Label(self, image=next(self.image_cycle))
        self.img_container.pack(fill="both", expand="yes")
        self.after(self.framerate, self.next_frame)

    def next_frame(self):
        """Update the image for each frame"""
        self.img_container.configure(image=next(self.image_cycle))
        self.after(self.framerate, self.next_frame)



if __name__ == '__main__':
    master = ttk.Window()
    master.current_theme = 'darkly'
    MainPage(master).pack(expand=True, fill='both')
    print()
    master.mainloop()
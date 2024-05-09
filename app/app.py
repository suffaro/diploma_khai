from settings import *
import login_page
from localization import MAIN_WINDOW
import ttkbootstrap as ttk
import tk
import darkdetect
from PIL import Image, ImageTk
from tkinter import filedialog, Canvas

class MainPage(ttk.Window):
    def __init__(self):
        super().__init__()

        self.title(f"{APP_NAME}_{VERSION}")
        self.geometry = ('900x600')
        self.minsize(600,600)
        self.maxsize(1200,900)

        self.current_theme = "darkly" if darkdetect.isDark() else "journal"
        self.style.theme_use(self.current_theme)

        # Create a custom style for the tabs

        customed_style = ttk.Style()
        customed_style.configure('Custom.TNotebook.Tab', padding=[12, 12], font=('Helvetica', 10))
        customed_style.configure('Custom.TNotebook', )
        notebook = ttk.Notebook(self, style='Custom.TNotebook')

        tab1 = MainTab(notebook)
        tab2 = ttk.Frame(notebook)
        tab3 = ttk.Frame(notebook)
        tab4 = ttk.Frame(notebook)
        tab5 = ttk.Frame(notebook)
        tab6 = ttk.Frame(notebook)

        notebook.add(tab1, text="Main page")
        notebook.add(tab2, text="Extensions")
        notebook.add(tab3, text="Q&A")
        notebook.add(tab4, text="Documentation")
        notebook.add(tab5, text="Settings")
        notebook.add(tab6, text="Account")

        notebook.pack(expand = True, fill = 'both')

        self.mainloop()


class AccountTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

class MainTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.master = master
        self.PICTURE_EXISTS = False

        self.columnconfigure(0, weight=2, uniform='a')
        self.columnconfigure(1, weight=1, uniform='a')
        self.rowconfigure(0, weight=4, uniform='a')
        self.rowconfigure(1, weight=1, uniform='a')


        self.upload_image_frame = ttk.Frame(self,
                                )
        self.upload_image_frame.columnconfigure(0, weight=1, uniform='a')
        self.upload_image_frame.rowconfigure(0, weight=1, uniform='a')

        
        self.upload_button = ttk.Button(self.upload_image_frame,
                                        text = "Upload Image",
                                        command=self.upload_image)
        
        self.upload_button.grid(row=0, column=0)

        self.upload_image_frame.grid(row = 0,column = 0, sticky='nsew')
        

        # widgets for image_frame
        

        self.settings_frame = ttk.Frame(self,)

        rofl = ["Model1", "Model2"]

        self.model_variable = ttk.StringVar()
        self.models_list = ttk.OptionMenu(self.settings_frame,
                                          variable=self.model_variable,
                                          )
        self.models_list.set_menu(rofl[0], *rofl)
        self.models_list.pack()

        rofl2 = ["classic", "fast", "best"]

        self.model_working_mode_variable = ttk.StringVar()
        self.working_mode_list = ttk.OptionMenu(self.settings_frame,
                                          variable=self.model_working_mode_variable,
                                          )
        self.working_mode_list.set_menu(rofl2[0], *rofl2)
        self.working_mode_list.pack()


        self.settings_frame.grid(row=0, column=1)


     

    def upload_image(self):
        path = filedialog.askopenfilename()
        print(path)
        if path:
            canvas_for_image = Canvas(self.upload_image_frame, height=200, width=200, borderwidth=0, highlightthickness=0)
            canvas_for_image.grid(row = 0, column = 0, sticky = 'nsew', padx=0, pady=0)

            image = Image.open(path)
            self.upload_button.grid_forget()
            canvas_for_image.image = ImageTk.PhotoImage(image.resize((self.winfo_width(), self.winfo_height())))
            canvas_for_image.create_image(0, 0, image=canvas_for_image.image, anchor='nw')
            if not self.PICTURE_EXISTS:
                self.upload_image_frame.bind('<Button-1>', self.upload_image)
                self.PICTURE_EXISTS = True
                MainPage.update()
                








if __name__ == '__main__':
    MainPage()
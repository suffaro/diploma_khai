from settings import *
import login_page
from localization import MAIN_WINDOW
import ttkbootstrap as ttk
import tk
import darkdetect



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

        tab1 = ttk.Frame(notebook)
        ttk.Entry(tab1).pack()
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



if __name__ == '__main__':
    MainPage()
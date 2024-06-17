import ttkbootstrap as ttk

class SlideWidget(ttk.Frame):
    def __init__(self, parent):
        super().__init__(master = parent, borderwidth = 2, border = 5)

        self.start_pos_x = 0.7
        self.start_pos_y = 0.8
        self.width = 0.35
        self.message = None

    def show_message(self, message):
        self.message = ttk.Label(self, text = message, wraplength = 150)
        self.message.pack(expand = True, fill = 'both')
        self.place(relx = self.start_pos_x, rely = self.start_pos_y, relwidth = self.width, relheight = 0.2)

    def destroy_message(self):
        if self.message:
            self.message.pack_forget()
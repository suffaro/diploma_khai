import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox, DatePickerDialog
import socket
import os
import database as db
import bcrypt
from datetime import date, timedelta
import time, os
from pathlib import Path
from ttkbootstrap.validation import validator, add_regex_validation, add_validation
import threading
import smtplib
from server import Server

mail_token = "87f8f8a3c4eb07c2ce13f7485cdd9ae0"
SERV_IP = {"IP": "127.0.0.1", "PORT": 65432}
CONFIG_FILE = 'D:\\diploma\\server-side\\config\\db_config.json'

database = db.Database(CONFIG_FILE)
database.connect()

class Client():
    def __init__(self):

        self.addr = (SERV_IP["IP"], SERV_IP['PORT'])
        self.buffer = 4096
        #self.run_client()
        


    def run_client(self):
        # create a socket object
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_ip = "127.0.0.1"  # replace with the server's IP address connect_client(), send_request(), close_connection(), update_application(), download_model(), send_payment(), send_logs() 
        server_port = 65432  # replace with the server's port number
        # establish connection with server
        client.connect((server_ip, server_port))

        try:
            while True:
                # get input message from user and send it to the server
                msg = input("Enter message: ")
                client.send(msg.encode("utf-8")[:self.buffer])

                # receive message from the server
                response = client.recv(self.buffer)
                response = response.decode("utf-8")

                # if server sent us "closed" in the payload, we break out of
                # the loop and close our socket
                if response.lower() == "closed":
                    break

        except Exception as e:
            print(f"Error: {e}")
        finally:
            # close client socket (connection to the server)
            client.close()

    def process_request(self, request: str, image_path=None) -> str:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        client.connect(self.addr)

        try:
            client.send(request.encode("utf-8")[:self.buffer])

            response = client.recv(self.buffer)
            response = response.decode("utf-8")

            return response
        
        except Exception as e:
            print(f"Error: {e}")
        finally:
            # close client socket (connection to the server)
            client.close()


# done
class AdminApp(ttk.Window):
    def __init__(self):
        super().__init__()

        self.geomerty = ("1100x600")
        self.minsize(600,600)
        self.maxsize(1400,1000)
        self.menu = MenuApp(self)
        self.title("Admin ImgProPlus")

        self.menu.pack_propagate(0)
        self.menu.pack(expand=True, fill='both')

        
    def run(self):
        self.mainloop()

# done
class MenuApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master = master)
        self.frames = {
            "Promotions" : PromotionTab(self), #PromotionTab(self),
            "Users": UsersTab(self),
            "Logs": LogsTab(self),
            "Payments": PaymentsTab(self),
            "Server": ServerTab(self),
            "Questions": QuestionsTab(self)
                       }
        self.create_widgets()

    def create_widgets(self):
        # Menu frame at the top
        menu_frame = ttk.Frame(self)
        menu_frame.pack(side='top', fill='x')
        
        # Container frame to hold the different content frames        
        # Dictionary to store the content frames

        
        # List of menu buttons and corresponding frame content
        buttons = [
            ("Promotions", self.create_frame1),
            ("Users", self.create_frame2),
            ("Logs", self.create_frame3),
            ("Payments", self.create_frame4),
            ("Server", self.create_frame5),
            ("Questions", self.create_frame6)
        ]
        
        # Create buttons
        for text, frame_func in buttons:
            button = ttk.Button(menu_frame, text=text, command=frame_func, bootstyle='info')
            button.pack(side='left', padx=1, pady=2, fill='x', expand=True)

        # Initialize with the first frame
        self.create_frame1()

    def create_frame1(self):
        self.show_frame("Promotions")

    def create_frame2(self):
        self.show_frame("Users")

    def create_frame3(self):
        self.show_frame("Logs")

    def create_frame4(self):
        self.show_frame("Payments")

    def create_frame5(self):
        self.show_frame("Server")
    
    def create_frame6(self):
        self.show_frame("Questions")



    def show_frame(self, frame_name):
        # Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()
        
        
        # Show the requested frame
        self.frames[frame_name].pack_propagate(0)
        self.frames[frame_name].pack(expand=True, fill='both')

# done
class PromotionTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master=master)

        self.create_widgets()
    
    def create_widgets(self):
        # Create Treeview widget
        self.tree = ttk.Treeview(self, columns=("id", "subscription_length", "price", "desc"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("subscription_length", text="Subscription Duration")
        self.tree.heading("price", text="Price")
        self.tree.heading("desc", text="Description")

        self.tree.column("id", width=50)
        self.tree.column("subscription_length", width=150)
        self.tree.column("price", width=100)
        self.tree.column("desc", width=300)

        self.refresh_table()

        self.tree.pack(expand=True, fill='both')

        # Delete button
        delete_button = ttk.Button(self, text="Delete", command = self.delete_promotion, bootstyle='danger')
        delete_button.pack(side='left', pady=10, padx=30, fill='both', expand=True)
        
        insert_button = ttk.Button(self, text="New Offer", command = lambda:  self.PromotionCreateWindow(master = self), bootstyle='warning')
        insert_button.pack(side='left', pady=10, padx=30, fill='both', expand=True)
        
        refresh_button = ttk.Button(self, text="Refresh", command=self.refresh_table)
        refresh_button.pack(side='left', pady=10, padx=30, fill='both', expand=True)



    def refresh_table(self):
        # Clear existing items in the Treeview
        self.tree.delete(*self.tree.get_children())

        # Sample data (replace with your data)
        query = "SELECT * from promotions"
        users = database.execute_query(query)
        if users:
            for user in users:
                modified_user = list(user)
                modified_user[2] = str(modified_user[2]) + "$"
                self.tree.insert("", "end", values=modified_user)
            

    def delete_promotion(self):
        selected_item = self.tree.selection()
        if not selected_item:
            Messagebox.show_error("No item selected", "Error", parent=self)
            return

        confirm = Messagebox.yesno("Confirm Delete", "Are you sure you want to delete this promotions(s)?", parent=self)
        test = True
        if confirm:
            for item in selected_item:
                promotion = self.tree.item(item, "values")[0]
                res = database.delete_promotion(promotion)
                if not res:
                    Messagebox.show_error(f"Error during deleting promotion - {promotion}.", "Error")
                    test = False
                self.tree.delete(item)
        if test:
            Messagebox.ok("All selected promotions are deleted!\nPage automatically refreshed.", "Info")
            self.refresh_table()


    class PromotionCreateWindow(ttk.Toplevel):
        def __init__(self, master):
            super().__init__(master)
            self.title("Create New Promotion Window")
            

            # Login Entry
            self.sub_label = ttk.Label(self, text="Sub duration:")
            self.sub_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.sub_entry = ttk.Entry(self)
            self.sub_entry.grid(row=0, column=1, padx=5, pady=5)

            add_regex_validation(self.sub_entry,'^\d{1,2}\s+months?$')

            # Password Entry
            self.price_label = ttk.Label(self, text="Price:")
            self.price_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.price_entry = ttk.Entry(self)
            self.price_entry.grid(row=1, column=1, padx=5, pady=5)

            add_validation(self.price_entry, validate_price)

             # Description Label
            self.desc_label = ttk.Label(self, text="Description:")
            self.desc_label.grid(row=2, column=0, padx=5, pady=5, sticky="nw")
            
            # Description Text Widget
            self.desc_text = ttk.Text(self, height=4, width=30)
            self.desc_text.grid(row=2, column=1, padx=5, pady=5, sticky="w")

            # Buttons
            self.close_button = ttk.Button(self, text="Close", command=lambda : self.destroy())
            self.close_button.grid(row=3, column=0, padx=5, pady=5, sticky="e")
            self.create_button = ttk.Button(self, text="Create", command=self.create_promotion)
            self.create_button.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        def show_date_picker(self, *args) -> str:
            result = DatePickerDialog(self, title="Select Sub. End Date", startdate=date.today() + timedelta(days=1))
            self.user_sub_date = result.date_selected


        def create_promotion(self):
            sub = self.sub_entry.get()
            price = self.price_entry.get()
            description = self.desc_text.get("1.0", ttk.END)
            # Add code to create promotion here

            result = database.insert_promotion(sub, price, description)
            if result:
                Messagebox.ok(f"Promotion added to database!\n Page automatically refreshed.", "Info")
                self.master.refresh_table()
            else:
                Messagebox.show_error("Promotion wasn't added to database! Something is wrong", "Error")

#done
class LogsTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master=master)
        self.log_file = str(Path(__file__).parent) + "\\logs\\server_side_logs.log"
        self.last_line_inserted = 0
        
        self.text_widget = ttk.Text(self, wrap="none")  # Set wrap to "none"
        self.text_widget.pack(fill="both", expand=True)
        self.rowconfigure(0, weight=1)  # Assign weight to the row
        
        refresh_button = ttk.Button(self, text="Refresh Logs", command=self.refresh_logs)
        refresh_button.pack(side="bottom", pady=5)

        self.text_widget.bind("<Enter>", lambda event: self.text_widget.tag_remove("last_added_text", "1.0", "end"))

        self.read_log_file(self.log_file)
        self.start_listening_file_changes()

    def read_log_file(self, file_path):
        with open(file_path, "r") as file:
            file.seek(self.last_line_inserted)  # Move the file pointer to the last line inserted
            log_contents = file.read()
            self.last_line_inserted = file.tell()
        if log_contents:
            self.text_widget.configure(state='normal')
            var1 = self.text_widget.index('end-1c')
            self.text_widget.insert(ttk.END, log_contents)
            var2 = self.text_widget.index('end-1c')
            self.text_widget.see(ttk.END)
            self.text_widget.tag_add("last_added_text", var1, var2)
            self.text_widget.tag_config("last_added_text", background="red")
            self.text_widget.tag_config("last_added_text", foreground="white")

            self.text_widget.configure(state='disabled')

    def refresh_logs(self):
        self.read_log_file(self.log_file)


    def detect_file_changes(self, file_path, interval=1):
        last_modified = os.path.getmtime(file_path)
        while True:
            current_modified = os.path.getmtime(file_path)
            if current_modified != last_modified:
                self.read_log_file(file_path)
                last_modified = current_modified
            time.sleep(interval)
    
    def start_listening_file_changes(self) -> None:
        threading.Thread(target=self.detect_file_changes, args=(self.log_file, 1)).start()

#done
class ServerTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master=master)
        self.server_thread = None
        self.server_running = False
        self.create_widgets()
        self.auto_refresh_interval = 1000  # in milliseconds

    def create_widgets(self):
        self.server_status_label = ttk.Label(self, text="Server Status: Not Running")
        self.server_status_label.grid(row=0, column=0, columnspan=2, pady=10, padx=10)
        
        self.request_label = ttk.Label(self, text="Input Client Request Above:")
        self.request_label.grid(row=1, column=0, columnspan=2, pady=10, padx=10)

        self.request_entry = ttk.Entry(self)
        self.request_entry.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky="ew")


        self.send_button = ttk.Button(self, text="Send Request", command=self.send_request)
        self.send_button.grid(row=3, column=0, pady=10, padx=10, sticky="ew")

        self.run_server_button = ttk.Button(self, text="Run Server", command=self.run_server, bootstyle="success")
        self.run_server_button.grid(row=3, column=1, pady=10, padx=10, sticky="ew")

        self.stop_server_button = ttk.Button(self, text="Stop Server", command=self.stop_server, bootstyle="danger")
        self.stop_server_button.grid(row=4, column=0, pady=10, padx=10, sticky="ew")

        self.refresh_button = ttk.Button(self, text="Refresh", command=self.refresh_server_status, bootstyle="warning")
        self.refresh_button.grid(row=4, column=1, pady=10, padx=10, sticky="ew")

        self.tip_button = ttk.Button(self, text="Show Tip", command=self.show_tip)
        self.tip_button.grid(row=5, column=0, pady=10, padx=10, sticky="ew")

        self.mini_logs_label = ttk.Label(self, text="Server output:")
        self.mini_logs_label.grid(row=6, column=0, columnspan=2, pady=10, padx=10)


        self.output_text = ttk.Text(self, state="disabled")
        self.output_text.grid(row=7, column=0,columnspan=2, pady=10, padx=10, sticky="nsew")

        # Configure column weights for proper resizing
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def run_server(self):
        if self.server_thread is None or not self.server_thread.is_alive():
            self.server_thread = threading.Thread(target=self.run_server_thread)
            self.server_thread.start()
            self.server_running = True
            self.auto_refresh()
        else:
            Messagebox.show_info("Server", "Server is already running.")

    def run_server_thread(self):
        try:
            self.serv = Server()
            self.serv.run_server()
            self.server_status_label.config(text="Server Status: Running")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.server_running = False
            self.server_status_label.config(text="Server Status: Not Running")

    def stop_server(self):
        if self.server_thread is not None and self.server_thread.is_alive():
            # implement logic here
            self.server_running = False
            self.server_thread = None
            if self.server_thread.is_alive():
                Messagebox.show_error("Server", "Failed to stop the server properly.")
            else:
                self.server_thread = None
                self.server_status_label.config(text="Server Status: Not Running")
        else:
            Messagebox.show_info("Server is not running.", "Server")

    def refresh_server_status(self):
        if self.server_thread is None or not self.server_thread.is_alive():
            self.server_status_label.config(text="Server Status: Not Running")
        else:
            self.server_status_label.config(text="Server Status: Running")

    def auto_refresh(self):
        self.refresh_server_status()
        if self.server_running:
            self.after(self.auto_refresh_interval, self.auto_refresh)

    def send_request(self):
        request = self.request_entry.get()
        if request:
            client = Client()
            response = client.process_request(request)
            self.output_text['state'] = 'normal'
            self.output_text.insert("1.0", response + "\n--------------------\n")
            self.output_text.see("1.0")
            self.output_text['state'] = 'disabled'
        else:
            Messagebox.show_warning("Input Error", "Please enter a request.")

    def show_tip(self):
        requests = [
            "UPD - update check (UPD|variable app_version)",
            "CLS - check login in system (CLS|variable username)",
            "UCV - user credentials verification (login) (UCV|variable username, variable password)",
            "CSV - credit status verification (CSV|variable username)",
            "TKN - token verification (TKN|variable token)",
            "SSV - user premium status verification (SSV|variable username)",
            "LOG - user send log with error (LOG|variable log_message)",
            "SCC - send confirmation code (SCC|variable username)",
            "IMG - send image for processing (IMG|variable image_name, variable config_dict, variable interrogate_method, variable username)",
            "VCC - verify confirmation code (VCC|variable username, variable code)",
            "MSG - user question (MSG|variable username, variable question)",
            "EXT - info about extensions (EXT)",
            "REG - register new user (REG|variable username, variable password, variable email)",
            "SUB - info about subscriptions (SUB|variable username)",
            "PAY - payment info (PAY|variable username, variable payment_info)",
            "DUP - download update (DUP|variable app_version)"
        ]
        
        tip_window = self.RequestTipWindow(self, requests)
        tip_window.mainloop()

    class RequestTipWindow(ttk.Toplevel):
        def __init__(self, master, requests):
            super().__init__(master)
            self.title("Request Tip")
            self.geometry("300x500")
            
            self.requests_text = ttk.Text(self, wrap="word")
            self.requests_text.pack(fill="both", expand=True, padx=10, pady=10)
            
            for request in requests:
                self.requests_text.insert(ttk.END, request + "\n")
            
            self.requests_text.configure(state="disabled")

# done
class PaymentsTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master=master)
        self.create_widgets()

    def create_widgets(self):
        # Create Treeview widget
        self.tree = ttk.Treeview(self, columns=("id", "username", "payment_date", "promotion_id"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("username", text="Username")
        self.tree.heading("payment_date", text="Payment Date")
        self.tree.heading("promotion_id", text="Promotion Id")

        
        self.tree.column("id", width=50)
        self.tree.column("username", width=150)
        self.tree.column("payment_date", width=100)
        self.tree.column("promotion_id", width=100)

        self.refresh_table()

        self.tree.pack(expand=True, fill='both')

        # Delete button
        delete_button = ttk.Button(self, text="Delete", command=self.delete_payment, bootstyle='danger')
        delete_button.pack(side='left', pady=10, padx=30, fill='both', expand=True)

        create_button = ttk.Button(self, text="Create Payment", command= lambda : self.PaymentCreateWindow(self), bootstyle='warning')
        create_button.pack(side='left', pady=10, padx=30, fill='both', expand=True)

        refresh_button = ttk.Button(self, text="Refresh", command=self.refresh_table, )
        refresh_button.pack(side='left', pady=10, padx=30, fill='both', expand=True)


    def refresh_table(self):
        # Clear existing items in the Treeview
        self.tree.delete(*self.tree.get_children())

        # Sample data (replace with your data)
        query = "SELECT * from payments"
        payments = database.execute_query(query)
        if payments:
            for payment in payments:
                self.tree.insert("", "end", values=payment)
        

    def delete_payment(self):
        selected_item = self.tree.selection()
        if not selected_item:
            Messagebox.show_error("No item selected", "Error", parent=self)
            return

        confirm = Messagebox.yesno("Confirm Delete", "Are you sure you want to delete this payments(s)?", parent=self)
        test = True
        if confirm:
            for item in selected_item:
                payment = self.tree.item(item, "values")[0]
                res = database.delete_payment(payment)
                if not res:
                    Messagebox.show_error(f"Error during deleting payment - {payment}.", "Error")
                    test = False
                self.tree.delete(item)
        if test:
            Messagebox.ok("All selected payments are deleted!\nPage automatically refreshed.", "Info")
            self.refresh_table()


    class PaymentCreateWindow(ttk.Toplevel):
        def __init__(self, master):
            super().__init__(master)
            self.title("Create Payment Window")
            

            self.payment_date = None
            # Login Entry
            self.username_label = ttk.Label(self, text="Username:")
            self.username_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.username_entry = ttk.Entry(self)
            self.username_entry.grid(row=0, column=1, padx=5, pady=5)

            # Password Entry
            self.date_label = ttk.Label(self, text="Payment Date:")
            self.date_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.date_button = ttk.Button(self, text='Pick a date', command = self.show_date_picker)
            self.date_button.grid(row=1, column=1, padx=5, pady=5)

            self.promotion_label = ttk.Label(self, text="Promotion ID:")
            self.promotion_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
            self.promotion_entry = ttk.Entry(self)
            self.promotion_entry.grid(row=2, column=1, padx=5, pady=5)


            # Buttons
            self.close_button = ttk.Button(self, text="Close", command=lambda : self.destroy())
            self.close_button.grid(row=3, column=0, padx=5, pady=5, sticky="e")
            self.create_button = ttk.Button(self, text="Create", command=self.create_payment)
            self.create_button.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        def show_date_picker(self, *args) -> str:
            result = DatePickerDialog(self, title="Select Sub. End Date", startdate=date.today() + timedelta(days=1))
            self.user_sub_date = result.date_selected



        def create_payment(self):
            username = self.username_entry.get()
            promotion = self.promotion_entry.get()

            result = database.add_payment(username, self.payment_date, promotion)
            if result:
                Messagebox.ok(f"Payment added to database!\nPage automatically refreshed.", "Info")
                self.master.refresh_table()
            else:
                Messagebox.show_error("User wasn't added to database! Something is wrong", "Error")

# done
class UsersTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master=master)
        self.create_widgets()

    def create_widgets(self):
        # Create Treeview widget
        self.tree = ttk.Treeview(self, columns=("id", "login", "sub_status"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("login", text="Login")
        self.tree.heading("sub_status", text="Subscription Status")

        self.refresh_table()

        self.tree.pack(expand=True, fill='both')

        # Delete button
        delete_button = ttk.Button(self, text="Delete", command=self.delete_user, bootstyle='danger')
        delete_button.pack(side='left', pady=10, padx=30, fill='both', expand=True)

        create_user_button = ttk.Button(self, text="Create User", command = lambda: self.UserCreateWindow(self), bootstyle='warning')
        create_user_button.pack(side='left', pady=10,padx=30, fill='both', expand=True)

        self.refresh_button = ttk.Button(self, text="Refresh", command=self.refresh_table)
        self.refresh_button.pack(side='left', pady=10,padx=30, fill='both', expand=True)

    def refresh_table(self):
        # Clear existing items in the Treeview
        self.tree.delete(*self.tree.get_children())

        # Sample data (replace with your data)
        query = "SELECT u.username, CASE WHEN s.username IS NULL THEN 'No Subscription' ELSE 'Has Subscription' END AS Subscription_Status FROM Users u LEFT JOIN Subscribers s ON u.username = s.username;"
        users = database.execute_query(query)
        i = 1
        if users:
            for user in users:
                self.tree.insert("", "end", values=(i, *user))
                i += 1
        

    def delete_user(self):
        selected_item = self.tree.selection()
        if not selected_item:
            Messagebox.show_error("No item selected", "Error", parent=self)
            return

        confirm = Messagebox.yesno("Confirm Delete", "Are you sure you want to delete this user(s)?", parent=self)
        test = True
        if confirm:
            for item in selected_item:
                username = self.tree.item(item, "values")[1]
                res = database.delete_user(username)
                if not res:
                    Messagebox.show_error(f"Error during deleting user - {username}.", "Error")
                    test = False
                self.tree.delete(item)
        if test:
            Messagebox.ok("All selected users are deleted!", "Info")


    class UserCreateWindow(ttk.Toplevel):
        def __init__(self, master):
            super().__init__(master)
            self.title("Create User Window")
            

            self.user_sub_date = None
            # Login Entry
            self.login_label = ttk.Label(self, text="Login:")
            self.login_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.login_entry = ttk.Entry(self)
            self.login_entry.grid(row=0, column=1, padx=5, pady=5)

            # Password Entry
            self.password_label = ttk.Label(self, text="Password:")
            self.password_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.password_entry = ttk.Entry(self)
            self.password_entry.grid(row=1, column=1, padx=5, pady=5)

            # Subscription Checkbutton
            self.subscription_var = ttk.IntVar()
            self.subscription_var.set(0)
            self.subscription_checkbutton = ttk.Checkbutton(self, text="Subscription", variable=self.subscription_var)
            self.subscription_checkbutton.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")
            self.subscription_var.trace_add('write', self.show_date_picker)

            # Buttons
            self.close_button = ttk.Button(self, text="Close", command=lambda : self.destroy())
            self.close_button.grid(row=3, column=0, padx=5, pady=5, sticky="e")
            self.create_button = ttk.Button(self, text="Create", command=self.create_account)
            self.create_button.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        def show_date_picker(self, *args) -> str:
            result = DatePickerDialog(self, title="Select Sub. End Date", startdate=date.today() + timedelta(days=1))
            self.user_sub_date = result.date_selected

        def create_account(self):
            login = self.login_entry.get()
            password = self.password_entry.get()
            subscribed = self.subscription_var.get()
            # Add code to create account here
            salt = bcrypt.gensalt()
            hash = bcrypt.hashpw(password.encode('utf-8'), salt)
            result = database.add_new_user(login, hash)
            added_sub = None
            if subscribed:
                added_sub = database.add_user_premium_status(login, self.user_sub_date)
            if result and added_sub or type(added_sub) != type(None):
                Messagebox.ok(f"User added to database!\nLogin: {login}\nPassword: {password}\nSubscribed: {'yes' if subscribed else 'no'}", "Info")
            else:
                Messagebox.show_error("User wasn't added to database! Something is wrong", "Error")

# done
class QuestionsTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master=master)

        self.create_widgets()

    def create_widgets(self):
        # Create Treeview widget
        self.tree = ttk.Treeview(self, columns=("id", "username", "request_text"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("username", text="Username")
        self.tree.heading("request_text", text="Request Text")

        self.tree.column("id", width=50)
        self.tree.column("username", width=100)
        self.tree.column("request_text", width=300)

        self.refresh_table()

        self.tree.pack(expand=True, fill='both')

        # Delete button
        delete_button = ttk.Button(self, text="Delete", command=self.delete_question, bootstyle='danger')
        delete_button.pack(side='left', pady=10, padx=30, fill='both', expand=True)

        create_user_button = ttk.Button(self, text="Write Response", command = self.create_writing_window, bootstyle='warning')
        create_user_button.pack(side='left', pady=10,padx=30, fill='both', expand=True)

        self.refresh_button = ttk.Button(self, text="Refresh", command=self.refresh_table)
        self.refresh_button.pack(side='left', pady=10,padx=30, fill='both', expand=True)


    def create_writing_window(self) -> None:
        try:
            email = self.tree.item(self.tree.selection(), "values")[1]
            self.ResponseCreateWindow(self, email)
        except IndexError:
            Messagebox.show_info("Select request first!", "Info")

    def refresh_table(self):
        try:
            # Clear existing items in the Treeview
            self.tree.delete(*self.tree.get_children())

            # Sample data (replace with your data)
            query = "select * from requests"
            questions = database.execute_query(query)
            for question in questions:
                self.tree.insert("", "end", values=question)
        except TypeError:
            pass

    def delete_question(self):
        selected_item = self.tree.selection()
        if not selected_item:
            Messagebox.show_error("No item selected", "Error", parent=self)
            return

        confirm = Messagebox.yesno("Confirm Delete", "Are you sure you want to delete this quesion(s)?", parent=self)
        test = True
        if confirm:
            for item in selected_item:
                req_id = self.tree.item(item, "values")[0]
                res = database.delete_request(req_id)
                if not res:
                    Messagebox.show_error(f"Error during deleting request - {req_id}.", "Error")
                    test = False
                self.tree.delete(item)
        if test:
            Messagebox.ok("All selected users are deleted!\nPage automatically refreshed.", "Info")
            self.refresh_table()


    class ResponseCreateWindow(ttk.Toplevel):
        def __init__(self, master, email):
            super().__init__(master = master)
            self.title("Send Response Window")

            self.email = email

            # Text Entry
            self.text_label = ttk.Label(self, text=f"Response Text to - {self.email}:")
            self.text_label.grid(row=0, column=0, padx=5, pady=5, sticky="nw")
            
            self.text_entry = ttk.Text(self, height=25, width=75)
            self.text_entry.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

            # Buttons
            self.send_button = ttk.Button(self, text="Send", command=self.send_response, bootstyle = 'warning')
            self.send_button.grid(row=2, column=0, padx=30, pady=5, sticky="nsew")

            self.close_button = ttk.Button(self, text="Close", command=self.destroy)
            self.close_button.grid(row=2, column=1, padx=30, pady=5, sticky="nsew")

            # Configure column and row weights to make text_entry expandable
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)
            self.grid_rowconfigure(1, weight=1)

        def send_response(self) -> None:
            result = self.text_entry.get("1.0", ttk.END)
            # sender = "Private Person <mailtrap@demomailtrap.com>"
            # receiver = f"A Test User <{username}>"

            # message = f"""\
            # Subject: Hi Mailtrap
            # To: {receiver}
            # From: {sender}

            #{result} 
            # Best wishes. ImgPlusPro Team."""

            # with smtplib.SMTP("live.smtp.mailtrap.io", 587) as server:
            #     server.starttls()
            #     server.login("api", "{mail_token}")
            #     server.sendmail(sender, receiver, message)
            send = True
            # 
            if send:
                answer = Messagebox.yesno(f"Responce to {self.email} was sent. Do you want to delete this record?.", "Info")
                if answer:
                    self.master.delete_question()
                    Messagebox.ok("Record was successfully deleted.\nPage was automatically refreshed.", "Info")
                    self.master.refresh_table()
                self.destroy()
            else:
                Messagebox.show_error(f"Responce to {self.email} wasn't sent. Something is wrong.", "Error")



@validator
def validate_price(event):
    try:
        x = float(event.postchangetext)
        if x > 0:
            return True
        return False
    except ValueError:
        return False


if __name__ == '__main__':
    AdminApp().run()

import socket
import threading
from my_logger import setup_logger
from database import Database
import os
import json

from PIL import Image

CONFIG_FILE = 'server-side/config/db_config.json'
APP_V = "1.0.2"
"""
    answer format
    {
        "status": ("failure", "success")
        "data": ("")
        "error_msg": "MESSAGE"            # in case of failure
    } 
"""


# UCV|rapperorwhat@gmail.com|Suma1l24_
"""request headers
    UPD - update check
    CLS - check login in system
    UCV - user credentials verification (login)
    CSV - credit status verification
    TKN - token verification
    SSV - user premium status verification
    LOG - user send log with error
    REG - register new user
    SCC - send confirmation code
    IMG - send image for processing
    VCC = verify confirmation code
    DUP - download update
"""
class Server():
    def __init__(self):

        self.addr_ip = "127.0.0.1"
        self.addr_port = 65432
        self.buffer = 4096

        self.logger = setup_logger('ServerLogger', "server_side_logs.log")

        self.images_dir = "uploaded_images"

        self.server_database = Database(CONFIG_FILE)
        self.server_database.connect()


        self.run_server()


    def handle_client(self, client_socket: socket.socket, addr) -> None:
        try:
            while True:
                # receive and print client messages
                request = client_socket.recv(self.buffer).decode("utf-8")
                request_list = request.split(sep = "|")
                print(request_list)
                if request_list[0] == "close":
                    client_socket.send("closed".encode("utf-8"))
                    break
                elif request_list[0] == 'CLS':
                    client_socket.send(self.process_request(request_list[1]))
                elif request_list[0] == 'UCV':
                    client_socket.send(self.user_verification(request_list[1], request_list[2]))
                elif request_list[0] == 'IMG':
                    prompts = self.process_image(request_list[1], request_list[2], request_list[3], request_list[4], client_socket)
                    client_socket.send(prompts)
                elif request_list[0] == 'TKN':
                    client_socket.send(self.verify_token(request_list[1]))
                elif request_list[0] == 'SSV':
                    client_socket.send(self.verify_user_premium(request_list[1]))
                elif request_list[0] == 'CSV':
                    client_socket.send(self.verify_credits(request_list[1]))
                elif request_list[0] == 'UPD':
                    client_socket.send(self.check_updates(request_list[1]))
                elif request_list[0] == 'REG':
                    client_socket.send(self.register_new_user(request_list[1], request_list[2], request_list[3]))
                elif request_list[0] == 'SCC':
                    client_socket.send(self.send_confirmation_code(request_list[1]))
                elif request_list[0] == 'VCC':
                    client_socket.send(self.verify_confirmation_code(request_list[1], request_list[2]))
                self.logger.info(f"Received: {request}")
                client_socket.close()
        except Exception as e:
            self.logger.error(f"Error when hanlding client: {e}")
        finally:
            client_socket.close()
            self.logger.info(f"Connection to client ({addr[0]}:{addr[1]}) closed")


    def process_image(self, image_name: str, config_dict: str, interrogate_method: str, username: str, socket : socket.socket) -> bytes:
        try:
            premium = self.server_database.verify_premium_status(username)
            credits = self.server_database.verify_user_credits(username)
            if not premium and credits == 0:
                return "no credit".encode('utf-8')
            elif not premium and credits > 0:
                credits = credits - 1
                if not self.server_database.decrement_user_credits(username):
                    return "no credit".encode('utf-8')
            self.receive_image(client_socket=socket, filename=image_name)
            from clip_interrogator import Interrogator, Config
            config_file = Config()
            list_with_configs = config_dict.split(sep=";")
            for pair in list_with_configs:
                key, value = pair.split(sep="=")
                if key == 'caption_max_length' or key == "chunk_size" or key == "flavor_intermediate_count":
                    setattr(config_file, key, int(value))
                    continue
                setattr(config_file, key, value)
            print(config_file)
            ci = Interrogator(config_file)

            image_path = os.path.join(self.images_dir, image_name)
            print("Image path")
            print(image_path)
            image = Image.open(image_path)
            print("Image opneed")

            if interrogate_method == 'best':
                prompts = ci.interrogate(image)
            elif interrogate_method == 'classic':
                prompts = ci.interrogate_classic(image)
            elif interrogate_method == 'fast':
                prompts = ci.interrogate_fast(image)
            elif interrogate_method == 'negative':
                prompts = ci.interrogate_negative(image)

            os.remove(image_path)

            print(prompts)
            return prompts.encode('utf-8')
        except Exception as e:
            self.logger.error(f"Error when processing image: {e}")





    def run_server(self):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # bind the socket to the host and port
            server.bind((self.addr_ip, self.addr_port))
            # listen for incoming connections
            server.listen()
            self.logger.info(f"Listening on {self.addr_ip}:{self.addr_port}")
            print("Server running!")

            while True:
                # accept a client connection
                client_socket, addr = server.accept()
                self.logger.info(f"Accepted connection from {addr[0]}:{addr[1]}")
                # start a new thread to handle the client
                thread = threading.Thread(target=self.handle_client, args=(client_socket, addr,))
                self.logger.info(f"{addr[0]}:{addr[1]} received {thread.name} for processing!")
                thread.start()
        except Exception as e:
            self.logger.error(f"Error: {e}")
        finally:
            server.close()

    def register_new_user(self, username: str, password: str, confirmation_code: str) -> bytes:
        pass

    def send_confirmation_code(self, username: str) -> bytes:
        try:
            result = self.server_database.generate_confirmation_code(username)
            # import smtplib

            # sender = "Private Person <mailtrap@demomailtrap.com>"
            # receiver = f"A Test User <{username}>"

            # message = f"""\
            # Subject: Hi Mailtrap
            # To: {receiver}
            # From: {sender}

            # Your confirmation code - {result}.It lasts 10 minutes. 
            # Don't send it to anybody."""

            # with smtplib.SMTP("live.smtp.mailtrap.io", 587) as server:
            #     server.starttls()
            #     server.login("api", "87f8f8a3c4eb07c2ce13f7485cdd9ae0")
            #     server.sendmail(sender, receiver, message)
            # return "sent".encode('utf-8')
            print(result)
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return "error".encode('utf-8')
        

    def verify_confirmation_code(self, username: str, code: str) -> bytes:
        pass

    def verify_user_premium(self, username: str) -> bytes:
        result = str(self.server_database.verify_premium_status(username))
        if result:
            return result.encode('utf-8')
        else:
            return "False".encode('utf-8')
    
    def check_updates(self, app_version: str) -> bytes:
        if app_version == APP_V:
            return "True".encode('utf-8')
        else:
            return APP_V.encode('utf-8')
        
    def download_update(self, app_version: str) -> None:
        pass

    def verify_credits(self, username: str) -> bytes:
        result = str(self.server_database.verify_user_credits(username)).encode('utf-8')
        return result
            
    def verify_token(self, token: str) -> bytes:
        if self.server_database.verify_auth_token(token):
            return "True".encode('utf-8')
        else:
            return "False".encode('utf-8')
        

    # requests : password confirm, email in the system, image for processing, buy premium, download model, send message to our team, update an app
    # 
    def process_request(self, request: str) -> bytes:
        return str(self.server_database.check_login_exists(request)).encode('utf-8')
    
    def user_verification(self, username: str, password: str) -> bytes:
        result = self.server_database.check_login_credentials(username=username, password = password)
        if result:
            token = self.server_database.add_auth_token(username=username, password=password)
            return token.encode('utf-8')
        else:
            return "False".encode('utf-8')

    # TODO: check verification
    def receive_image(self, client_socket: socket.socket, filename: str) -> None:
        try:
            os.makedirs(self.images_dir, exist_ok=True)
            file_path = os.path.join(self.images_dir, filename)
            client_socket.send("Got your image".encode('utf-8'))
            with open(file_path, 'wb') as f:
                while True:
                    # Receive image data chunk from the client
                    image_chunk = client_socket.recv(self.buffer)
                    if image_chunk.endswith(b"<END>"):
                        f.write(image_chunk[:-5])  # Remove the <END> marker
                        break
                    # Write the received image data chunk to the file
                    f.write(image_chunk)
            self.logger.info(f"Image {filename} saved successfully.")
            client_socket.send(f"Image {filename} received and saved.".encode("utf-8"))
        except Exception as e:
            self.logger.error(f"Error receiving image: {e}")
            client_socket.send(f"Error receiving image: {e}".encode("utf-8"))





if __name__ == '__main__':
    serv = Server()
import socket
import threading
from my_logger import setup_logger
from database import Database
import os
import bcrypt
import pathlib
from PIL import Image
import sys
import json

sys.path.insert(0, '..\\clip')



DB_CONFIG_FILE = str(pathlib.Path(__file__).parent) + '\config\db_config.json'
SERV_CONFIG_FILE = str(pathlib.Path(__file__).parent) + '\config\serv_config.json'
API_TOKENS = str(pathlib.Path(__file__).parent) + '\config\env.json'

with open(API_TOKENS, 'r') as file:
    config = json.load(file)

    LIQPAY_TOKEN = config.get("LIQPAY_TOKEN")
    EMAIL_PROVIDER_TOKEN = config.get("EMAIL_PROVIDER_TOKEN")


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
    SCC - send confirmation code
    IMG - send image for processing
    VCC - verify confirmation code
    MSG - user question
    EXT - info about extensions

    REG - register new user
    SUB - info about subscriptions
    PAY - payment info
    DUP - download update
    RMV - remove token

    RES - reset password
"""
class Server():
    def __init__(self):

        with open(SERV_CONFIG_FILE, 'r') as file:
            config = json.load(file)

            self.addr_ip = config.get("IP")
            self.addr_port = config.get("PORT")
            self.buffer = config.get("MAX_CHUNK_SIZE")
            self.max_conn = config.get("MAX_CONNECTIONS")
            self.online = config.get("ONLINE")

        if not os.path.exists(os.path.dirname(os.path.realpath(__file__)) + "\\logs"):
            os.mkdir(os.path.dirname(os.path.realpath(__file__)) + "\\logs")
        self.logger = setup_logger(logger_name="Server Logger", logger_file=".\logs\server_side_logs.log")

        self.images_dir = "uploaded_images"

        self.server_database = Database(DB_CONFIG_FILE)
        self.server_database.connect()




    def handle_client(self, client_socket: socket.socket, addr) -> None:
        try:   # receive and print client messages
            request = client_socket.recv(self.buffer).decode("utf-8")
            request_list = request.split(sep = "|")
            if request_list[0] == "close":
                client_socket.send("closed".encode("utf-8"))
            elif request_list[0] == 'CLS':
                client_socket.send(self.user_exists(request_list[1]))
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
                client_socket.send(self.register_new_user(request_list[1], request_list[2]))
            elif request_list[0] == 'SCC':
                client_socket.send(self.send_confirmation_code(request_list[1]))
            elif request_list[0] == 'VCC':
                client_socket.send(self.verify_confirmation_code(request_list[1], request_list[2]))
            elif request_list[0] == 'MSG':
                client_socket.send(self.apply_request(request_list[1], request_list[2]))
            elif request_list[0] == 'EXT':
                client_socket.send(self.get_models())
            elif request_list[0] == 'SUB':
                client_socket.send(self.get_subscriptions(request_list[1]))
            elif request_list[0] == 'PAY':
                client_socket.send(self.get_payment_info(request_list[1]))
            elif request_list[0] == 'DUP':
                client_socket.send(self.download_update())
            elif request_list[0] == 'RMV':
                client_socket.send(self.remove_token(request_list[1]))
            elif request_list[0] == 'RES':
                client_socket.send(self.reset_password(request_list[1], request_list[2]))
            else:
                client_socket.send("Error".encode("utf-8"))
            self.logger.info(f"Received: {request}")
            client_socket.close()
        except Exception as e:
            self.logger.error(f"Error when hanlding client: {e}")
        finally:
            self.logger.info(f"Connection to client ({addr[0]}:{addr[1]}) closed")

    def get_models(self) -> bytes:
        try:
            models = self.server_database.get_models()
            if not models:
                return "Error".encode('utf-8')
            answer = ""
            for model in models:
                answer = answer + f"{model[0]};{model[1]};{model[2]}" + "|"
            return answer[:-1].encode("utf-8")
        except Exception as e:
            self.logger(f"Error during models - {e}.")
            return ""

    def reset_password(self, username: str, new_password: str) -> bytes:
        try:
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            return str(self.server_database.reset_password(username, hashed)).encode('utf-8')
        except Exception as e:
            self.logger(f"Error during reset password - {e}.")

    def get_subscriptions(self, locale) -> bytes:
        subscriptions = self.server_database.get_subscriptions(locale)
        if not subscriptions:
            return "Error".encode('utf-8')
        answer = ""
        for subscription in subscriptions:
            answer = answer + f"{subscription[0]};{subscription[1]};{subscription[2]}" + "|"
        return answer[:-1].encode("utf-8")
    

    def get_payment_info(self, username: str) -> bytes:
        return str(self.server_database.add_payment(username)).encode('utf-8')
    
    def remove_token(self, token: str) -> bytes:
        return str(self.server_database.remove_auth_token(token)).encode('utf-8')

    def process_image(self, image_name: str, config_dict: str, interrogate_method: str, username: str, socket: socket.socket) -> bytes:
        """
        Process an image using the specified configuration and interrogation method.

        Args:
            image_name (str): The name of the image file to be processed.
            config_dict (str): A string containing configuration settings in the format 'key=value;key=value;...'.
            interrogate_method (str): The interrogation method to use ('best', 'classic', 'fast', or 'negative').
            username (str): The username of the user requesting the image processing.
            socket (socket.socket): The socket object used for communication.

        Returns:
            bytes: The prompts generated by the image interrogation process, encoded as bytes.

        Raises:
            Exception: If an error occurs during the image processing.

        This function performs the following steps:
        1. Verifies the user's premium status and available credits.
        2. Receives the image file from the client.
        3. Parses the configuration settings from the config_dict string.
        4. Creates an instance of the Interrogator class with the specified configuration.
        5. Loads the image file and performs the specified interrogation method.
        6. Removes the temporary image file.
        7. Returns the generated prompts as bytes.

        If the user is not a premium user and has no credits, it returns "no credit" as bytes.
        If the user is not a premium user but has credits, it decrements the user's credits.
        If an error occurs during the process, it logs the error message.
        """
        try:
            # Verify user's premium status and available credits
            premium = self.server_database.verify_premium_status(username)
            credits = self.server_database.verify_user_credits(username)
            if not premium and credits == 0:
                return "no credit".encode('utf-8')
            elif not premium and credits > 0:
                credits = credits - 1
                if not self.server_database.decrement_user_credits(username):
                    return "no credit".encode('utf-8')

            # Receive the image file from the client
            self.receive_image(client_socket=socket, filename=image_name)

            from clip_interrogator import Interrogator, Config

            # Parse configuration settings
            config_file = Config()
            config_file.clip_model_path = os.path.join(os.path.dirname(__file__), 'models')
            list_with_configs = config_dict.split(sep=";")
            for pair in list_with_configs:
                key, value = pair.split(sep="=")
                if key == 'caption_max_length' or key == "chunk_size" or key == "flavor_intermediate_count":
                    setattr(config_file, key, int(value))
                else:
                    setattr(config_file, key, value)

            # Create an instance of the Interrogator class
            ci = Interrogator(config_file)

            # Load the image and perform the specified interrogation method
            image_path = os.path.join(self.images_dir, image_name)
            image = Image.open(image_path)
            if interrogate_method == 'best':
                prompts = ci.interrogate(image)
            elif interrogate_method == 'classic':
                prompts = ci.interrogate_classic(image)
            elif interrogate_method == 'fast':
                prompts = ci.interrogate_fast(image)
            elif interrogate_method == 'negative':
                prompts = ci.interrogate_negative(image)

            # Remove the temporary image file
            os.remove(image_path)

            # Return the generated prompts as bytes
            return prompts.encode('utf-8')

        except Exception as e:
            self.logger.error(f"Error when processing image: {e}")

    def apply_request(self, message: str, username: str) -> bytes:
        try:
            result = self.server_database.add_request(username, message)
            return str(result).encode('utf-8')
        except Exception as e:
            self.logger.error(f"Error when adding user request: {e}")
            return "False"



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

    def register_new_user(self, username: str, password: str) -> bytes:
        salt = bcrypt.gensalt()
        pass_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        result = self.server_database.add_new_user(username, pass_hash)
        if result:
            return "done".encode('utf-8')
        return "error"

    def send_confirmation_code(self, username: str) -> bytes:
        try:
            result = self.server_database.generate_confirmation_code(username)
            self.logger.info(f"Generated confirmation code: {result} for user {username}")
            import smtplib

            sender = "Private Person <mailtrap@demomailtrap.com>"
            receiver = f"A Test User <{username}>"

            message = f"""\
            Subject: Hi Mailtrap
            To: {receiver}
            From: {sender}

            This is a test e-mail message."""

            with smtplib.SMTP("live.smtp.mailtrap.io", 587) as server:
                server.starttls()
                server.login("api", EMAIL_PROVIDER_TOKEN)
                server.sendmail(sender, receiver, message)
            return "send".encode('utf-8')
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return f"Error sending email: Contact administrator please.".encode('utf-8')
        

    def verify_confirmation_code(self, username: str, code: str) -> bytes:
        result = self.server_database.verify_confirmation_code(username, code)
        return str(result).encode('utf-8')

    def verify_user_premium(self, username: str) -> bytes:
        result = str(self.server_database.verify_premium_status(username))
        return result.encode('utf-8')
    
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
    def user_exists(self, username: str) -> bytes:
        return str(self.server_database.check_login_exists(username)).encode('utf-8')
    
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
    serv.run_server()
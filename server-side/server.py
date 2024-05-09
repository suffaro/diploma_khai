import socket
import threading
from my_logger import setup_logger
from database import Database

class Server():
    def __init__(self):

        self.addr_ip = "127.0.0.1"
        self.addr_port = 65432
        self.buffer = 4096

        self.logger = setup_logger('ServerLogger', "server_side_logs.log")


        self.run_server()


    def handle_client(self, client_socket, addr):
        try:
            while True:
                # receive and print client messages
                request = client_socket.recv(self.buffer).decode("utf-8")
                if request.lower() == "close":
                    client_socket.send("closed".encode("utf-8"))
                    break
                elif request.lower()[:5] == 'login':
                    client_socket.send(self.process_request(request).encode('utf-8'))
                self.logger.info(f"Received: {request}")
                # convert and send accept response to the client
                response = "accepted"
                client_socket.send(response.encode("utf-8"))
        except Exception as e:
            self.logger.error(f"Error when hanlding client: {e}")
        finally:
            client_socket.close()
            self.logger.info(f"Connection to client ({addr[0]}:{addr[1]}) closed")


    def run_server(self):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # bind the socket to the host and port
            server.bind((self.addr_ip, self.addr_port))
            # listen for incoming connections
            server.listen()
            self.logger.info(f"Listening on {self.addr_ip}:{self.addr_port}")

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


    # requests : password confirm, email in the system, image for processing, buy premium, download model, send message to our team, update an app
    # 
    def process_request(self, request) -> str:
        pass




if __name__ == '__main__':
    serv = Server()
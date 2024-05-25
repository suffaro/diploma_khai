import socket
import os
from settings import SERV_IP


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

                print(f"Received: {response}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            # close client socket (connection to the server)
            client.close()
            print("Connection to server closed")

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
            print("Connection to server closed")

    def send_image(self, request: str, image_path: str) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(self.addr)
            s.send(request.encode('utf-8'))
            response = s.recv(self.buffer).decode('utf-8')
            if response == "no credit":
                return response
            print(response)
            with open(image_path, 'rb') as f:
                file_data = f.read()
            s.sendall(file_data)
            s.sendall(b"<END>")
            print("waiting for response..")
            response = s.recv(self.buffer).decode('utf-8')
            print(response)
            prompts = s.recv(self.buffer).decode('utf-8')
            s.close()
            return prompts
        except Exception as e:
            print(f"Error: {e}")


if __name__ == '__main__':
    client = Client().run_client()
    
    # test of image sending
    
    # client = Client()
    # file = "C:\\Users\\nyokayo\\Desktop\\picture.jpg"
    # request = "IMG|picta.jpg|caption_max_length=32;caption_model_name=blip-large;caption_offload=True;clip_model_name=ViT-L-14/openai;clip_model_path=None;clip_offload=False;download_cache=True;chunk_size=2048;flavor_intermediate_count=2048|fast|rapperorwhat@gmail.com"
    # res = client.send_image(request, file)
    # print(res)
    #client.send_image("")
    # import os
    # print(os.path.getsize(file))
    
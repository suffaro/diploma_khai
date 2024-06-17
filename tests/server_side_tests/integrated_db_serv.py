import sys
sys.path.insert(0, "d:\\diploma\\server-side")
print(sys.path)

import pytest
import socket
import threading
import os
import bcrypt
from server import Server
from database import Database




def create_test_image():
    from PIL import Image

# Define the size of the square image
    size = 500

    # Create a new square image
    img = Image.new('RGB', (size, size), 'red')

    # Save the image as test_image.jpg
    img.save('uploaded_images\\test_image.jpg')




# Fixture to set up the test database
@pytest.fixture(scope="module")
def test_db():
    # Setup the test database
    db = Database('config.json')  # Ensure you have a test config file
    db.connect()
    
    # Populate with some test data if needed
    # db.add_new_user('test_user', bcrypt.hashpw('password'.encode('utf-8'), bcrypt.gensalt()))

    yield db

    # Teardown the test database
    db.close()

# Fixture to set up the server
@pytest.fixture(scope="module")
def server(test_db):
    server_instance = Server()
    server_instance.server_database = test_db  # Use the test database
    server_thread = threading.Thread(target=server_instance.run_server, daemon=True)
    server_thread.start()
    
    yield server_instance
    
    # No explicit teardown needed since daemon=True ensures it exits with the main program

def test_register_new_user(server):
    # Use a socket to communicate with the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server.addr_ip, server.addr_port))
    
    request = "REG|new_user|password"
    client_socket.send(request.encode("utf-8"))
    response = client_socket.recv(server.buffer).decode("utf-8")
    
    assert response == "done"
    
    # Cleanup: Remove the user from the database after the test
    server.server_database.delete_user("new_user")
    client_socket.close()

def test_user_verification(server):
    # Pre-register a user in the test database
    username = "test_user"
    password = "password"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    server.server_database.add_new_user(username, hashed_password)
    
    # Use a socket to communicate with the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server.addr_ip, server.addr_port))
    
    request = f"UCV|{username}|{password}"
    client_socket.send(request.encode("utf-8"))
    response = client_socket.recv(server.buffer).decode("utf-8")
    
    assert response == server.server_database.add_auth_token(username, password)
    
    # Cleanup: Remove the user from the database after the test
    server.server_database.delete_user(username)
    client_socket.close()

def test_process_image(server):


    # Pre-register a user in the test database
    username = "test_user"
    password = "password"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    server.server_database.add_new_user(username, hashed_password)  # Ensure the user has credits

    # Use a socket to communicate with the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server.addr_ip, server.addr_port))

    image_name = "test_image.jpg"
    image_path = os.path.join(server.images_dir, image_name)

    config = "caption_max_length=32;caption_model_name=blip-large"
    request = f"IMG|{image_name}|{config}|best|{username}"
    client_socket.send(request.encode("utf-8"))
    response = client_socket.recv(server.buffer).decode("utf-8")

    # Assuming the server should return some prompt or "no credit"
    print(f"Server response: {response}")  # Print the server's response (prompt or response)
    assert response != "no credit"

    # Cleanup: Remove the user and the image from the database and filesystem after the test
    server.server_database.delete_user(username)



if __name__ == '__main__':
    #create_test_image()
    pass
import socket
from PIL import Image

def send_image(img: Image, host: str = '127.0.0.1', port: int = 999):
    s = socket.socket()
    s.connect((host, port))
    img_data = img._repr_png_()
    s.sendall(img_data)
    s.shutdown(socket.SHUT_WR)  # close socket for writing, receiving is still possible
    print(f'Sent {len(img_data) / 1024:,.1f} kB of image data.')
    b_data = b''
    while recv_data := s.recv(2048):
        b_data += recv_data
    print(f'Server response: {b_data.decode()}')
    # maybe check server response for server side errors etc. and add return value for this function?

# use like: send_image(Image.open('test.png'))
import io
import queue
import socket
import threading

import cv2
import numpy as np
from PIL import Image

def image_viewer(q: queue.Queue):
    while True:
        try:
            img_name, img = q.get(block=True, timeout=.1)  # poll every 0.1 seconds
            print(f'Image viewer: displaying `{img_name}`!')
            cv2.imshow('Image preview', img)
        except queue.Empty:
            ...  # no new image to display
        key = cv2.pollKey()  # non-blocking
        if key & 0xff == ord('q'):
            cv2.destroyAllWindows()
            print('Image viewer was closed')
            return

def serve_forever(host: str, port: int, img_dir: str = 'C:/Users/my_user/stream_images/', img_format: str = '.png'):
    q = queue.Queue()
    img_viewer = threading.Thread(target=image_viewer, args=(q,))
    img_viewer.start()

    with socket.socket() as s:
        s.bind((host, port))
        s.listen(1)
        count = 0
        print('The server is ready')
        while True:
            conn, addr = s.accept()
            count = count + 1
            img_name = img_dir + 'frame' + str(count) + img_format
            print (f'Client connected: {addr}')
            img = b''
            while data := conn.recv(2048):
                img += data
            conn.sendall('Thank you for connecting'.encode())  # maybe use return codes for success, error etc.?
            conn.close()
            pil_img = Image.open(io.BytesIO(img))  # might want to save to disk?
            np_img = np.asarray(pil_img)
            np_img = cv2.rotate(np_img, cv2.ROTATE_90_CLOCKWISE)
            q.put((img_name, np_img))
            print (f'Client at {addr} disconnected after receiving {len(img) / 1024:,.1f} kB of data.')

if __name__ == '__main__':
    serve_forever('127.0.0.1', 999)
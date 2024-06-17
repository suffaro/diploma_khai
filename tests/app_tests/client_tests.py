import sys
sys.path.insert(0, "d:\\diploma\\gui")


import unittest
from unittest.mock import patch, MagicMock
import socket
from client import Client  # Replace with the actual module name
from settings import SERV_IP


class TestClient(unittest.TestCase):
    
    def setUp(self):
        self.client = Client()

    @patch('client.socket.socket')
    def test_process_request(self, mock_socket):
        mock_socket_inst = MagicMock()
        mock_socket.return_value = mock_socket_inst

        # Mocking connect and recv
        mock_socket_inst.recv.return_value = b'success'

        response = self.client.process_request("UCV|username|password")
        
        mock_socket_inst.connect.assert_called_with((SERV_IP["IP"], SERV_IP['PORT']))
        mock_socket_inst.send.assert_called_with(b'UCV|username|password')
        self.assertEqual(response, "success")

    @patch('client.socket.socket')
    def test_send_image_no_credit(self, mock_socket):
        mock_socket_inst = MagicMock()
        mock_socket.return_value = mock_socket_inst

        # Mocking connect, recv, and sendall
        mock_socket_inst.recv.side_effect = [b'no credit']

        response = self.client.send_image("IMG|picta.jpg|caption_max_length=32;caption_model_name=blip-large|best|username", "path/to/image.jpg")

        mock_socket_inst.connect.assert_called_with((SERV_IP["IP"], SERV_IP['PORT']))
        mock_socket_inst.send.assert_any_call(b'IMG|picta.jpg|caption_max_length=32;caption_model_name=blip-large|best|username')
        self.assertEqual(response, "no credit")

    @patch('client.socket.socket')
    def test_send_image_success(self, mock_socket):
        mock_socket_inst = MagicMock()
        mock_socket.return_value = mock_socket_inst

        # Mocking connect, recv, and sendall
        mock_socket_inst.recv.side_effect = [b'ok', b'Image received and saved.', b'Generated prompts']

        with patch('builtins.open', unittest.mock.mock_open(read_data=b'image data')):
            response = self.client.send_image("IMG|picta.jpg|caption_max_length=32;caption_model_name=blip-large|best|username", "path/to/image.jpg")

        mock_socket_inst.connect.assert_called_with((SERV_IP["IP"], SERV_IP['PORT']))
        mock_socket_inst.send.assert_any_call(b'IMG|picta.jpg|caption_max_length=32;caption_model_name=blip-large|best|username')
        mock_socket_inst.sendall.assert_any_call(b'image data')
        mock_socket_inst.sendall.assert_any_call(b'<END>')
        self.assertEqual(response, "Generated prompts")

    @patch('client.socket.socket')
    @patch('builtins.input', side_effect=["Hello", "closed"])
    def test_run_client(self, mock_input, mock_socket):
        mock_socket_inst = MagicMock()
        mock_socket.return_value = mock_socket_inst

        mock_socket_inst.recv.side_effect = [b'Hello, Client', b'closed']

        self.client.run_client()

        mock_socket_inst.connect.assert_called_with((self.client.addr))
        self.assertTrue(mock_socket_inst.send.called)
        self.assertTrue(mock_socket_inst.recv.called)


if __name__ == '__main__':
    unittest.main()

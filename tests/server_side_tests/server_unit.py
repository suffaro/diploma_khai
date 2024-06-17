
import sys
sys.path.insert(0, "d:\\diploma\\server-side")
print(sys.path)



import pytest
from unittest.mock import patch, MagicMock
from server import Server  # Replace with the actual module name
from database import Database
import os
import socket





@pytest.fixture
def server():
    server_instance = Server()
    yield server_instance
    # Teardown: Close database connection after each test


def test_get_models(server):
    # Mock the database response
    server.server_database.get_models = MagicMock(return_value=[("model1", "description1", "version1"),
                                                                ("model2", "description2", "version2")])
    # Call the method under test
    models = server.get_models()

    # Check if the method returns the expected data
    assert models == b'model1;description1;version1|model2;description2;version2'


def test_reset_password(server):
    # Mock the database response
    server.server_database.reset_password = MagicMock(return_value=True)

    # Call the method under test
    result = server.reset_password("username", "new_password")

    # Check if the method returns the expected result
    assert result == b'True'


def test_get_subscriptions(server):
    # Mock the database response
    server.server_database.get_subscriptions = MagicMock(return_value=[("subscription1", "description1", "price1"),
                                                                       ("subscription2", "description2", "price2")])
    # Call the method under test
    subscriptions = server.get_subscriptions("locale")

    # Check if the method returns the expected data
    assert subscriptions == b'subscription1;description1;price1|subscription2;description2;price2'


def test_register_new_user(server):
    # Mock the database response
    server.server_database.add_new_user = MagicMock(return_value=True)

    # Call the method under test
    result = server.register_new_user("username", "password")

    # Check if the method returns the expected result
    assert result == b'done'


def test_send_confirmation_code(server):
    # Mock the database response
    server.server_database.generate_confirmation_code = MagicMock(return_value="123456")

    # Call the method under test
    result = server.send_confirmation_code("username")

    # Check if the method returns the expected result
    assert result == b'send'


def test_verify_confirmation_code(server):
    # Mock the database response
    server.server_database.verify_confirmation_code = MagicMock(return_value=True)

    # Call the method under test
    result = server.verify_confirmation_code("username", "123456")

    # Check if the method returns the expected result
    assert result == b'True'


def test_verify_user_premium(server):
    # Mock the database response
    server.server_database.verify_premium_status = MagicMock(return_value=True)

    # Call the method under test
    result = server.verify_user_premium("username")

    # Check if the method returns the expected result
    assert result == b'True'


def test_check_updates(server):
    # Call the method under test
    result = server.check_updates("1.0.2")

    # Check if the method returns the expected result
    assert result == b'True'


def test_verify_credits(server):
    # Mock the database response
    server.server_database.verify_user_credits = MagicMock(return_value=10)

    # Call the method under test
    result = server.verify_credits("username")

    # Check if the method returns the expected result
    assert result == b'10'


def test_verify_token(server):
    # Mock the database response
    server.server_database.verify_auth_token = MagicMock(return_value=True)

    # Call the method under test
    result = server.verify_token("token")

    # Check if the method returns the expected result
    assert result == b'True'


def test_user_exists(server):
    # Mock the database response
    server.server_database.check_login_exists = MagicMock(return_value=True)

    # Call the method under test
    result = server.user_exists("username")

    # Check if the method returns the expected result
    assert result == b'True'


def test_user_verification(server):
    # Mock the database response
    server.server_database.check_login_credentials = MagicMock(return_value=True)
    server.server_database.add_auth_token = MagicMock(return_value="token")

    # Call the method under test
    result = server.user_verification("username", "password")

    # Check if the method returns the expected result
    assert result == b'token'


# Add more test cases for other methods as needed
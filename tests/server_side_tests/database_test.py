import sys
sys.path.insert(0, "d:\\diploma\\server-side")
print(sys.path)


import pytest
from unittest.mock import patch, MagicMock
from database import Database
import json

# Mock config file content
mock_config = {
    "host": "localhost",
    "user": "testuser",
    "password": "testpassword",
    "database": "testdb"
}

@patch('builtins.open', new_callable=MagicMock)
@patch('json.load', return_value=mock_config)
def test_load_config(mock_json_load, mock_open):
    db = Database("config.json")
    db.load_config("config.json")
    assert db.host == "localhost"
    assert db.user == "testuser"
    assert db.password == "testpassword"
    assert db.database == "testdb"

@patch.object(Database, 'execute_query', return_value=True)
def test_add_new_user_success(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.add_new_user("testuser", "testhash")
    assert result is True

@patch.object(Database, 'execute_query', side_effect=Exception("DB error"))
def test_add_new_user_failure(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    with pytest.raises(Exception) as excinfo:
        result = db.add_new_user("testuser", "testhash")
    assert excinfo.value.args[0] == 'DB error'
    
@patch.object(Database, 'execute_query', return_value=[("hashed_password",)])
def test_check_login_credentials_success(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    with patch('bcrypt.checkpw', return_value=True):
        result = db.check_login_credentials("testuser", "testpassword")
        assert result is True

@patch.object(Database, 'execute_query', return_value=[("hashed_password",)])
def test_check_login_credentials_failure(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    with patch('bcrypt.checkpw', return_value=False):
        result = db.check_login_credentials("testuser", "testpassword")
        assert result is False

@patch.object(Database, 'execute_query', return_value=False)
def test_check_login_credentials_no_user(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.check_login_credentials("testuser", "testpassword")
    assert result is False

@patch.object(Database, 'execute_query', return_value=True)
def test_remove_auth_token_success(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.remove_auth_token("testtoken")
    assert result is True

@patch.object(Database, 'execute_query', return_value=False)
def test_remove_auth_token_failure(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.remove_auth_token("testtoken")
    assert result is False

@patch.object(Database, 'execute_query', return_value=True)
def test_add_auth_token(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.add_auth_token("testuser", "testpassword")
    assert result is not None

@patch.object(Database, 'execute_query', return_value=[(1,)])
def test_verify_auth_token_success(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.verify_auth_token("testtoken")
    assert result is True

@patch.object(Database, 'execute_query', return_value=[(0,)])
def test_verify_auth_token_failure(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.verify_auth_token("testtoken")
    assert result is False

@patch.object(Database, 'execute_query', return_value=[])
def test_check_login_exists(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.check_login_exists("testuser")
    assert result is True

@patch.object(Database, 'execute_query', return_value=True)
def test_add_user_premium_status_success(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.add_user_premium_status("testuser", "2024-12-31")
    assert result is True

@patch.object(Database, 'execute_query', return_value=False)
def test_add_user_premium_status_failure(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.add_user_premium_status("testuser", "2024-12-31")
    assert result is False

@patch.object(Database, 'execute_query', return_value=True)
def test_add_payment_success(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.add_payment("testuser", "2024-12-31", "promo1")
    assert result is True

@patch.object(Database, 'execute_query', return_value=False)
def test_add_payment_failure(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.add_payment("testuser", "2024-12-31", "promo1")
    assert result is False

@patch.object(Database, 'execute_query', return_value=True)
def test_delete_promotion_success(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.delete_promotion("promo1")
    assert result is True

@patch.object(Database, 'execute_query', return_value=False)
def test_delete_promotion_failure(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.delete_promotion("promo1")
    assert result is False

@patch.object(Database, 'execute_query', return_value=True)
def test_insert_promotion_success(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.insert_promotion("6 months", "49.99", "Half year subscription")
    assert result is True

@patch.object(Database, 'execute_query', return_value=False)
def test_insert_promotion_failure(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.insert_promotion("6 months", "49.99", "Half year subscription")
    assert result is False

@patch.object(Database, 'execute_query', return_value=True)
def test_delete_user_success(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.delete_user("testuser")
    assert result is True

@patch.object(Database, 'execute_query', return_value=False)
def test_delete_user_failure(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.delete_user("testuser")
    assert result is False

@patch.object(Database, 'execute_query', return_value=True)
def test_delete_payment_success(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.delete_payment("payment1")
    assert result is True

@patch.object(Database, 'execute_query', return_value=False)
def test_delete_payment_failure(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.delete_payment("payment1")
    assert result is False

@patch.object(Database, 'execute_query', return_value=True)
def test_add_request_success(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.add_request("testuser", "This is a test request")
    assert result is True

@patch.object(Database, 'execute_query', return_value=False)
def test_add_request_failure(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.add_request("testuser", "This is a test request")
    assert result is False

@patch.object(Database, 'execute_query', return_value=[("2024-12-31",)])
def test_verify_premium_status_success(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.verify_premium_status("testuser")
    assert result == "2024-12-31"

@patch.object(Database, 'execute_query', return_value=[])
def test_verify_premium_status_failure(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.verify_premium_status("testuser")
    assert result is False

@patch.object(Database, 'execute_query', return_value=[("6 months", "49.99", "Half year subscription")])
def test_get_subscriptions(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.get_subscriptions("EN")
    assert result == [("6 months", "49.99", "Half year subscription")]

@patch.object(Database, 'execute_query', return_value=True)
def test_reset_password_success(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.reset_password("testuser", "newpassword")
    assert result is True

@patch.object(Database, 'execute_query', return_value=False)
def test_reset_password_failure(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.reset_password("testuser", "newpassword")
    assert result is False

@patch.object(Database, 'execute_query', return_value=[("user1",), ("user2",)])
def test_get_all_users(mock_execute_query):
    db = Database("config.json")
    db.logger = MagicMock()
    result = db.execute_query("SELECT * FROM users")
    assert result == [("user1",), ("user2",)]

import sys
sys.path.insert(0, "d:\\diploma\\server-side")
sys.path.insert(0, "d:\\diploma\\app")



import pytest
from app import MenuApp
import login_page as AuthWindow
import admin_app as AdminPanel
import ttkbootstrap as ttk

@pytest.fixture
def app(qtbot):
    """Fixture to create an instance of the app for testing."""
    app = MenuApp(ttk.Window())
    qtbot.addWidget(app)
    return app

def test_TA01(app, qtbot):
    """Тестування змоги системи авторизувати користувачів."""
    assert app.auth_window.isVisible()
    assert "Login" in app.auth_window.title()

def test_TA02(app, qtbot):
    """Тестування авторизації користувача за допомогою логіну і паролю."""
    app.auth_window.login_input.setText("user_login")
    app.auth_window.password_input.setText("user_password")
    qtbot.mouseClick(app.auth_window.login_button, qtbot.LeftButton)
    assert app.main_interface.isVisible()

def test_TA03(app, qtbot):
    """Тестування авторизації користувача за допомогою пошти і паролю."""
    app.auth_window.email_input.setText("user@example.com")
    app.auth_window.password_input.setText("user_password")
    qtbot.mouseClick(app.auth_window.login_button, qtbot.LeftButton)
    assert app.main_interface.isVisible()

def test_TA04(app, qtbot):
    """Тестування реєстрації користувача за допомогою пошти і паролю."""
    app.auth_window.register_button.click()
    app.auth_window.email_input.setText("newuser@example.com")
    app.auth_window.password_input.setText("new_password")
    qtbot.mouseClick(app.auth_window.register_button, qtbot.LeftButton)
    assert "Confirmation Code" in app.auth_window.title()

def test_TA05(app, qtbot):
    """Тестування функціоналу для керування аккаунтом користувача."""
    app.auth_window.login_input.setText("user_login")
    app.auth_window.password_input.setText("user_password")
    qtbot.mouseClick(app.auth_window.login_button, qtbot.LeftButton)
    assert app.account_page.isVisible()

def test_TA06(app, qtbot):
    """Тестування можливості користувачів налаштовувати параметри облікового запису."""
    app.auth_window.login_input.setText("user_login")
    app.auth_window.password_input.setText("user_password")
    qtbot.mouseClick(app.auth_window.login_button, qtbot.LeftButton)
    app.account_page.settings_button.click()
    assert app.settings_page.isVisible()

def test_TA07(app, qtbot):
    """Тестування функціоналу керування користувачами та їх обліковими записами."""
    app.auth_window.login_input.setText("admin")
    app.auth_window.password_input.setText("admin_password")
    qtbot.mouseClick(app.auth_window.login_button, qtbot.LeftButton)
    assert app.admin_panel.isVisible()
    app.admin_panel.manage_users_button.click()
    assert app.admin_panel.user_management_page.isVisible()

def test_TA08(app, qtbot):
    """Тестування створення тестового користувача та перегляду списку існуючих користувачів."""
    app.auth_window.login_input.setText("admin")
    app.auth_window.password_input.setText("admin_password")
    qtbot.mouseClick(app.auth_window.login_button, qtbot.LeftButton)
    app.admin_panel.manage_users_button.click()
    app.admin_panel.user_management_page.create_user("testuser", "testuser@example.com")
    assert "testuser" in app.admin_panel.user_management_page.user_list

def test_TA09(app, qtbot):
    """Тестування відображення підтверджувального вікна при видаленні користувача."""
    app.auth_window.login_input.setText("admin")
    app.auth_window.password_input.setText("admin_password")
    qtbot.mouseClick(app.auth_window.login_button, qtbot.LeftButton)
    app.admin_panel.manage_users_button.click()
    app.admin_panel.user_management_page.select_user("testuser")
    qtbot.mouseClick(app.admin_panel.user_management_page.delete_button, qtbot.LeftButton)
    assert app.admin_panel.user_management_page.confirmation_dialog.isVisible()

def test_TA10(app, qtbot):
    """Тестування можливості адміністраторів керувати запитаннями та відповідями."""
    app.auth_window.login_input.setText("admin")
    app.auth_window.password_input.setText("admin_password")
    qtbot.mouseClick(app.auth_window.login_button, qtbot.LeftButton)
    app.admin_panel.manage_questions_button.click()
    assert app.admin_panel.question_management_page.isVisible()

def test_TA11(app, qtbot):
    """Тестування можливості адміністраторів керувати платежами."""
    app.auth_window.login_input.setText("admin")
    app.auth_window.password_input.setText("admin_password")
    qtbot.mouseClick(app.auth_window.login_button, qtbot.LeftButton)
    app.admin_panel.manage_payments_button.click()
    assert app.admin_panel.payment_management_page.isVisible()

def test_TA12(app, qtbot):
    """Тестування сторінки управління платежами."""
    app.auth_window.login_input.setText("admin")
    app.auth_window.password_input.setText("admin_password")
    qtbot.mouseClick(app.auth_window.login_button, qtbot.LeftButton)
    app.admin_panel.manage_payments_button.click()
    assert app.admin_panel.payment_management_page.isVisible()

def test_TA13(app, qtbot):
    """Тестування сторінки деталізації платежів."""
    app.auth_window.login_input.setText("admin")
    app.auth_window.password_input.setText("admin_password")
    qtbot.mouseClick(app.auth_window.login_button, qtbot.LeftButton)
    app.admin_panel.manage_payments_button.click()
    app.admin_panel.payment_management_page.select_payment("payment_1")
    assert app.admin_panel.payment_detail_page.isVisible()

def test_TA14(app, qtbot):
    """Тестування можливості адміністраторів переглядати логи серверу."""
    app.auth_window.login_input.setText("admin")
    app.auth_window.password_input.setText("admin_password")
    qtbot.mouseClick(app.auth_window.login_button, qtbot.LeftButton)
    app.admin_panel.view_logs_button.click()
    assert app.admin_panel.logs_page.isVisible()

if __name__ == '__main__':
    from xd import run_tests
    run_tests("admin_tests", 14, "13.28")
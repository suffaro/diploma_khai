import sys
sys.path.insert(0, "d:\\diploma\\app")
print(sys.path)


import unittest
from unittest.mock import patch, MagicMock
import ttkbootstrap as ttk
from login_page import LoginPage, ApplicationConfiguration, LOGIN_PAGE

class TestLoginPage(unittest.TestCase):
    
    def setUp(self):
        # Setup a root window for the test
        self.root = ttk.Window()
        self.root.current_theme = 'journal'
        self.app_configuration = ApplicationConfiguration()
        self.login_page = LoginPage(master=self.root)
        self.root.login_page = self.login_page
        self.root.form_main_page = self.form_main_page

    def form_main_page(self):
        print("Imitation of main_page_packing")
    
    def tearDown(self):
        # Clean up the root window
        self.root.destroy()

    def test_initialization(self):
        # Test if LoginPage initializes with all components
        self.assertIsInstance(self.login_page, ttk.Frame)
        self.assertIsNotNone(self.login_page.change_theme_button)
        self.assertIsNotNone(self.login_page.login_email_entry)
        self.assertIsNotNone(self.login_page.login_password_entry)
        self.assertIsNotNone(self.login_page.login_button)

    @patch('client.Client.process_request', return_value="False")
    @patch('ttkbootstrap.dialogs.Messagebox.show_error')
    def test_login_failure(self, mock_messagebox, mock_process_request):
        # Test login failure case
        self.login_page.email_variable.set("test@example.com")
        self.login_page.password_variable.set("wrongpassword")
        self.login_page.login_to_app()
        
        mock_process_request.assert_called_with("UCV|test@example.com|wrongpassword")
        mock_messagebox.assert_called_with(LOGIN_PAGE["message_wrong_email_or_pass"][self.app_configuration.locale], "Error", parent=self.login_page)

    @patch('client.Client.process_request', return_value="sometoken")
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_login_success(self, mock_open, mock_process_request):
        # Test login success case
        self.login_page.email_variable.set("test@example.com")
        self.login_page.password_variable.set("correctpassword")
        self.login_page.login_to_app()

        mock_process_request.assert_called_with("UCV|test@example.com|correctpassword")
        mock_open.assert_called_with("token", 'w')
        mock_open().write.assert_called_with("test@example.com|sometoken")

    def test_change_theme(self):
        # Test theme change
        initial_theme = self.login_page.current_theme
        print(initial_theme)
        self.login_page.change_current_theme()
        new_theme = self.login_page.current_theme

        self.assertNotEqual(initial_theme, new_theme)

    @patch('login_page.RegistrationWindow')
    def test_registration_button(self, mock_registration_window):
        # Test registration button triggers RegistrationWindow
        self.login_page.registration_button.invoke()
        mock_registration_window.assert_called_with(self.login_page)

    @patch('login_page.ForgotPasswordWindow')
    def test_forgot_password_button(self, mock_forgot_password_window):
        # Test forgot password button triggers ForgotPasswordWindow
        self.login_page.forgot_password_button.invoke()
        mock_forgot_password_window.assert_called_with(self.login_page)

if __name__ == '__main__':
    unittest.main()


import sys
sys.path.insert(0, "d:\\diploma\\server-side")
sys.path.insert(0, "d:\\diploma\\app")



import pytest
from app import PaymentWindow
import ttkbootstrap as ttk

@pytest.fixture
def app(qtbot):
    """Fixture to create an instance of the app for testing."""
    app = PaymentWindow(ttk.Window())
    qtbot.addWidget(app)
    return app

def test_TP01(app, qtbot):
    """Тестування можливості придбання підписки."""
    qtbot.mouseClick(app.subscription_page_button, qtbot.LeftButton)
    subscriptions = app.get_available_subscriptions()
    app.select_subscription(subscriptions[0])
    qtbot.mouseClick(app.purchase_button, qtbot.LeftButton)
    assert app.subscription_activated.isVisible()

def test_TP02(app, qtbot):
    """Тестування можливості перегляду наявних підписок."""
    qtbot.mouseClick(app.view_subscriptions_button, qtbot.LeftButton)
    assert app.subscription_list.isVisible()
    for subscription in app.subscription_list:
        assert subscription.has_price_and_discount_info()

def test_TP03(app, qtbot):
    """Тестування можливості керування підпискою."""
    qtbot.mouseClick(app.manage_subscription_button, qtbot.LeftButton)
    app.select_subscription_to_manage(app.active_subscription)
    qtbot.mouseClick(app.change_settings_button, qtbot.LeftButton)
    app.update_subscription_settings({"renewal": False, "notification": True})
    qtbot.mouseClick(app.save_settings_button, qtbot.LeftButton)
    assert app.settings_updated.isVisible()

if __name__ == "__main__":
    from xd import run_tests
    run_tests("payme_tests", 3, "3.01")
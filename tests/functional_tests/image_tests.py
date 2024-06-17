import sys
sys.path.insert(0, "d:\\diploma\\server-side")
sys.path.insert(0, "d:\\diploma\\app")


import pytest
from app import MainTab
import ttkbootstrap as ttk

@pytest.fixture
def app(qtbot):
    """Fixture to create an instance of the app for testing."""
    app = MainTab()
    qtbot.addWidget(app)
    return app

def test_TO01(app, qtbot):
    """Тестування можливості системи перетворювати різні формати зображень."""
    formats = ["image.jpg", "image.png", "image.bmp"]
    for format in formats:
        app.load_image(format)
        qtbot.mouseClick(app.convert_button, qtbot.LeftButton)
        assert app.image_converted.isVisible()

def test_TO02(app, qtbot):
    """Тестування функціоналу масштабування та обрізки зображень."""
    app.load_image("image.jpg")
    qtbot.mouseClick(app.resize_button, qtbot.LeftButton)
    qtbot.mouseClick(app.crop_button, qtbot.LeftButton)
    assert app.image_resized.isVisible()
    assert app.image_cropped.isVisible()

def test_TO05(app, qtbot):
    """Тестування можливості збереження результатів обробки зображень."""
    app.load_image("image.jpg")
    qtbot.mouseClick(app.process_button, qtbot.LeftButton)
    qtbot.mouseClick(app.save_button, qtbot.LeftButton)
    assert app.save_dialog.isVisible()

def test_TO06(app, qtbot):
    """Тестування опрацювання зображень за допомогою завантажених моделей обробки."""
    app.load_image("image.jpg")
    app.select_model("model_1")
    qtbot.mouseClick(app.process_button, qtbot.LeftButton)
    assert app.processed_image.isVisible()

def test_TO07(app, qtbot):
    """Тестування можливості вибору типу опрацювання зображень."""
    qtbot.mouseClick(app.processing_type_button, qtbot.LeftButton)
    app.select_processing_type("Type_1")
    assert app.processing_type_selected.isVisible()

def test_TO08(app, qtbot):
    """Тестування відображення повідомлення про недостатню кількість кредитів чи відсутність підписки."""
    app.select_processing_type("Server")
    qtbot.mouseClick(app.process_button, qtbot.LeftButton)
    assert app.insufficient_credits_message.isVisible()

def test_TO09(app, qtbot):
    """Тестування відображення повідомлення про перевірку потужності ПК."""
    app.select_processing_type("Local")
    qtbot.mouseClick(app.process_button, qtbot.LeftButton)
    assert app.checking_pc_power_message.isVisible()

def test_TO10(app, qtbot):
    """Тестування можливості налаштування опрацювання зображень."""
    qtbot.mouseClick(app.settings_button, qtbot.LeftButton)
    app.adjust_settings({"brightness": 50, "contrast": 30})
    qtbot.mouseClick(app.apply_settings_button, qtbot.LeftButton)
    assert app.settings_applied.isVisible()

def test_TO11(app, qtbot):
    """Тестування можливості збереження результатів опрацювання зображень за заданими PROMPTs."""
    app.load_image("image.jpg")
    qtbot.mouseClick(app.process_button, qtbot.LeftButton)
    qtbot.mouseClick(app.save_prompt_button, qtbot.LeftButton)
    app.set_prompt("example_prompt")
    assert app.prompt_saved.isVisible()

def test_TO12(app, qtbot):
    """Тестування можливості завантаження нових моделей обробки зображень."""
    qtbot.mouseClick(app.load_model_button, qtbot.LeftButton)
    app.upload_model("new_model")
    assert app.model_uploaded.isVisible()

if __name__ == '__main__':
    from xd import run_tests
    run_tests("image_tests", 12, "21.04")


# Програмне забезпечення попередньої обробки зображень для визначення promt   на основі clip  моделі
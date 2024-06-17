import sys
sys.path.insert(0, "d:\\diploma\\server-side")
sys.path.insert(0, "d:\\diploma\\app")


import pytest
from app import MenuApp, DocumentationTab
import ttkbootstrap as ttk

@pytest.fixture
def menu_app(qtbot):
    """Fixture to create an instance of MenuApp for testing."""
    root = ttk.Window()
    root.current_theme = 'journal'
    window = MenuApp(root)
    qtbot.addWidget(window)
    return window

def test_ti1(menu_app, qtbot):
    """Test the possibility for users to read the application documentation."""
    # Simulate the transition to the application documentation page
    menu_app.show_documentation()
    
    # Check if the documentation page is displayed correctly
    assert menu_app.documentation_page.isVisible()
    assert "Documentation" in menu_app.documentation_page.title()
    # Add more assertions to check the contents of the documentation page


def test_ti2(menu_app, qtbot):
    """Test the functionality of the image scaling and cropping page."""
    # Simulate the transition to the image scaling and cropping page
    menu_app.show_scaling_and_cropping()
    
    # Check if the scaling and cropping page is displayed correctly
    assert menu_app.scaling_and_cropping_page.isVisible()
    
    # Set the parameters for scaling and cropping
    menu_app.scaling_and_cropping_page.set_dimensions(800, 600)
    menu_app.scaling_and_cropping_page.set_scaling_mode('Fit')
    menu_app.scaling_and_cropping_page.set_cropping_mode('Center')
    
    # Simulate pressing the "Apply" button
    qtbot.mouseClick(menu_app.scaling_and_cropping_page.apply_button, qtbot.LeftButton)
    
    # Verify that the changes take effect
    assert menu_app.scaling_and_cropping_page.apply_changes()

if __name__ == "__main__":
    from xd import run_tests
    run_tests("infor_tests", 2, "0.22")




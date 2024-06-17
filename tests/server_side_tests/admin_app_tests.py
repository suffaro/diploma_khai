import sys
sys.path.insert(0, "d:\\diploma\\server-side")
print(sys.path)


import pytest
import tkinter as tk
from admin_app import UsersTab, PaymentsTab, QuestionsTab, ServerTab

@pytest.fixture
def root():
    return tk.Tk()

def test_payments_tab_creation(root):
    payments_tab = PaymentsTab(root)
    payments_tab.pack()
    
    assert payments_tab.winfo_exists() == 1
    assert isinstance(payments_tab.tree, tk.ttk.Treeview)
    assert len(payments_tab.tree.get_children()) == 1  # Assuming the table is empty initially

    payments_tab.master.destroy()

def test_users_tab_creation(root):
    users_tab = UsersTab(root)
    users_tab.pack()
    
    assert users_tab.winfo_exists() == 1
    assert isinstance(users_tab.tree, tk.ttk.Treeview)
    assert len(users_tab.tree.get_children()) == 5  # Assuming the table is empty initially

    users_tab.master.destroy()

def test_questions_tab_creation(root):
    questions_tab = QuestionsTab(root)
    questions_tab.pack()
    
    assert questions_tab.winfo_exists() == 1
    assert isinstance(questions_tab.tree, tk.ttk.Treeview)
    assert len(questions_tab.tree.get_children()) == 0  # Assuming the table is empty initially

    questions_tab.master.destroy()

def test_request_tip_window_creation(root):
    requests = ["Request 1", "Request 2", "Request 3"]
    request_tip_window = ServerTab.RequestTipWindow(root, requests)

    assert request_tip_window.winfo_exists() == 1
    assert isinstance(request_tip_window.requests_text, tk.Text)
    request_tip_window.requests_text.configure(state="normal")  # Enable state to check text
    text_content = request_tip_window.requests_text.get("1.0", tk.END)
    
    for request in requests:
        assert request in text_content

    request_tip_window.master.destroy()

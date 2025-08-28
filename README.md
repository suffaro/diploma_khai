# 🎓 Diploma Project — Image Prompt Generator

An application with a **client-server architecture** designed to generate prompts for image generation models.

---

## 🧩 Architecture Overview

### 📦 Database
- **MySQL**  
  Used to store:
  - Client accounts
  - Credits
  - Subscription data

### 🧠 Backend
- **Hugging Face API** – For downloading models used in prompt recognition  
- **Custom Prompt Library** – Handles prompt generation logic  
- **Server:** Written in Python  
  - Uses custom request headers over **HTTPS**

### 🎨 Frontend
- **ttkbootstrap** (Python UI framework)

### 💳 Payment System
- **LiqPay API**  
  - Generates QR codes for payments  
  - Provides secure payment links

---

## 🚀 Getting Started

You can run the application in one of two ways:
1. Use the provided **Dockerfile**.
2. Clone the repository and create the **MySQL database** manually from scratch.

---

## 🖥️ Client Application

The client is packaged as an `.exe` file for ease of use.  
If you want to run it locally **without connecting to the server**, you can:
- Open `main.py`
- Modify the code to **bypass the authentication process**

---

## ⚠️ Notes

- This project was developed as part of a diploma thesis.
- It is currently not under active development.

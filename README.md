# Diploma Project
An application with a client-server architecture for generating image prompts.
Database: MySQL (used to store client data, including credits and subscriptions)
Backend: Hugging Face API for model downloading (prompt recognition), combined with a custom library for delivering prompts. The server is written in Python and uses custom request headers over HTTPS.
Frontend: ttkbootstrap (Python)
Payment System: LiqPay API (QR code generation and payment link creation)

To use the application, either run it via the provided Dockerfile or clone the repository and create the database from scratch.

The client application is designed to run as an .exe file. If you want to run it locally without a server, you can modify the code in main.py to bypass the authentication process.


If you're looking for more information about this application, please open .pdf file in the root directory of the repo.

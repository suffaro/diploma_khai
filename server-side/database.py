import mysql.connector
import logging
from mysql.connector import Error
import json
import os
from my_logger import setup_logger
from hashlib import sha256
from datetime import date, timedelta, datetime
import bcrypt
from random import randint

class Database:
    def __init__(self, config_file):
        self.host = None
        self.user = None
        self.password = None
        self.database = None
        self.connection = None
        self.logger = setup_logger("DatabaseLogger", "server_side_logs")

        self.load_config(config_file)

    def load_config(self, config_file):
        try:
            with open(config_file, 'r') as file:
                config = json.load(file)
                self.host = config.get('host')
                self.user = config.get('user')
                self.password = config.get('password')
                self.database = config.get('database')
        except Exception as e:
            self.logger.error(f"Error loading configuration from JSON file: {e}")

    def add_new_user(self, username: str, password_hash: str) -> bool:
        try:
            query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            self.execute_query(query, (username, password_hash))
            self.logger.info(f"Added new user with Login: {username} and Pass_Hash: {password_hash}")
            # adding record to credits
            query = "INSERT INTO Credits(username) VALUES (%s)"
            self.execute_query(query, (username, ))
            self.logger.info(f"Added record in credit system for user: {username}")
            return True
        except Error as e:
            self.logger.error(f"Error executind adding new user. Query - {query}: {e}")
            return False
    
    def check_login_credentials(self, username: str, password: str) -> bool:
        try:
            query = "SELECT password FROM users WHERE username = %s"
            results = self.execute_query(query, (username,))
            
            if results[0][0]:
                stored_hash = results[0][0].encode('utf-8')
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                    self.logger.info(f"Login credentials for user {username} verified.")
                    return True
                else:
                    self.logger.info(f"Login credentials for user {username} not verified. Password hashes aren't the same.")
                    return False
            else:
                self.logger.info(f"Login credentials for user {username} not verified. No record found")
                return False
        except Error as e:
            self.logger.error(f"Error executing login credentials check for user {username}: {e}")
            return False
    
    # create table for this function
    def add_auth_token(self, username: str, password: str) -> str:
        try:
            today_date = date.today().strftime('%Y-%m-%d')
            reference_string = username + password + today_date
            hashed_token = sha256(reference_string.encode()).hexdigest()
            query = "INSERT INTO auth_tokens (token, start_date, end_date, username) VALUES (%s,%s,%s,%s)"
            if self.execute_query(query, (hashed_token, today_date, (date.today() + timedelta(days=21)).strftime('%Y-%m-%d'), username)):
                return hashed_token
            else:
                return None
        except Error as e:
            self.logger.error(f"Something went wrong during add_auth_token function. Error - {e}")
        
    def verify_auth_token(self, token: str) -> bool:
        try:
            query = "SELECT COUNT(*) FROM auth_tokens WHERE token = %s"
            results = self.execute_query(query, (token,))
            self.logger.info('verify_auth_token executed succesfully!')
            if results[0][0] == 1:
                return True
            else: return False
        except Error as e:
            self.logger.error(f"Something went wrong during verify_auth_token function. Error - {e}")

    def check_login_exists(self, username: str) -> bool:
        try:
            query = "SELECT authority FROM users WHERE username = %s"
            results = self.execute_query(query, (username,))
            self.logger.info('Check_login_exists executed succesfully!')
            if results[0][0] == 1:
                return True
            else: return False
        except Error as e:
            self.logger.error(f"Something went wrong during Check_login_exists function. Error - {e}")

    # i need subscription table for monitoring subscriptions of users
    # userid + subscription id + beginning date + cancelling date
    def add_user_premium_status(self, username: str) -> bool:
        pass

    # for this i need to check monobank api
    def add_payment(self):
        pass

    def add_request(self, username: str, requestText: str) -> bool:
        try:
            query = "INSERT INTO Requests (username, requestText) VALUES (%s, %s)"
            results = self.execute_query(query, (username, requestText))
            self.logger.info('add_request executed succesfully!')
            if results:
                return True
            else:
                return False
        except Error as e:
            self.logger.error(f"Something went wrong during add_request function. Error - {e}")

    def verify_premium_status(self, username: str) -> str | bool:
        try:
            query = "SELECT end_date FROM Subscribers WHERE username = %s"
            results = self.execute_query(query, (username,))
            self.logger.info('verify_premium_status executed succesfully!')
            if results[0][0]:
                return results[0][0]
            else: return False
        except Error as e:
            self.logger.error(f"Something went wrong during verify_premium_status function. Error - {e}")

    def verify_user_credits(self, username: str) -> str:
        try:
            query = "SELECT credits FROM Credits WHERE username = %s"
            results = self.execute_query(query, (username,))
            self.logger.info('verify_user_credits executed succesfully!')
            if results[0][0]:
                return results[0][0]
            else: return False
        except Error as e:
            self.logger.error(f"Something went wrong during verify_user_credits function. Error - {e}")

    def generate_confirmation_code(self, username: str) -> str:
        try:
            code = str(randint(100000, 999999))
            query = "INSERT INTO confirmation_codes(username, code, expiration_date) VALUES (%s, %s, %s)"
            expiration_date = datetime.now() + timedelta(minutes=10)
            results = self.execute_query(query, (username, code, expiration_date))
            self.logger.info('generate_confirmation_code executed succesfully!')
            if results:
                return code
            else: return False
        except Error as e:
            self.logger.error(f"Something went wrong during generate_confirmation_code function. Error - {e}")

    def verify_user_credits(self, username: str) -> str | bool:
        try:
            query = "SELECT credits FROM Credits WHERE username = %s"
            results = self.execute_query(query, (username,))
            self.logger.info('verify_user_credits executed succesfully!')
            if results[0][0]:
                return results[0][0]
            else: return False
        except Error as e:
            self.logger.error(f"Something went wrong during verify_user_credits function. Error - {e}")

    def decrement_user_credits(self, username: str) -> bool:
        try:
            query = "UPDATE credits SET credits = credits - 1 WHERE username = %s"
            results = self.execute_query(query, (username,))
            self.logger.info('decrement_user_credits executed succesfully!')
            if results:
                return True
            else: return False
        except Error as e:
            self.logger.error(f"Something went wrong during decrement_user_credits function. Error - {e}")

    def verify_confirmation_code(self, username: str, code: str) -> bool:
        try:
            query = "select code from confirmation_codes where username = %s and code = %s"
            results = self.execute_query(query, (username,code))
            self.logger.info('verify_confirmation_code executed succesfully!')
            if results:
                return True
            else: return False
        except Error as e:
            self.logger.error(f"Something went wrong during verify_confirmation_code function. Error - {e}")

    
    # all payments
    # all messages
    # add payment
    # add user premium status
    # update user's subscription
    

    

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                self.logger.info("Connected to MySQL database")
        except Error as e:
            self.logger.error(f"Error connecting to MySQL database: {e}")

    def close(self):
        if self.connection.is_connected():
            self.connection.close()
            self.logger.info("Connection to MySQL database closed")


    def execute_query(self, query, params=None) -> list | bool:
        """
        Execute a MySQL query and return the results.

        Args:
            query (str): The SQL query to execute.
            params (tuple or list, optional): A tuple or list of parameters to substitute into the query.

        Returns:
            list: A list of tuples containing the rows returned by the query.
            bool: In case if operaion was addition (returns bool True)
        """
       
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            self.connection.commit()
            return results if results else True

        except mysql.connector.Error as error:
            self.logger.error(f"Error executing query: {error}")
            return False

        finally:
            cursor.close()
            # db.close()




    def test(self,):
        query = "INSERT INTO Subscriptions (subscriptionID, codeName, amount) values (%s, %s, %s)"
        params = (1, "subscriber", '10')

        results = self.execute_query(query, params)
        if results:
            print("1")
        else:
            print('2')
        print(results)






# Example usage:
if __name__ == "__main__":
    config_file = 'server-side/config/db_config.json'
    db = Database(config_file)

    db.connect()

    # pass_hash = "$2b$12$N7hbRSm84721Lqslr29i.eEvqcxNA.WA6anBPNnniiNnnFYDD/KkO"

    # # query = "SELECT * FROM Users"
    username = 'rapperorwhat@gmail.com'
    # results = db.check_login_exists(username)

    # print(results)

    # print(db.check_login_credentials(username, pass_hash))

    #query = "select end_date from Subscribers"
    #db.execute_query(query, (username, ))

    # print(db.verify_premium_status(username))

    db.close()



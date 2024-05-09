import mysql.connector
import logging
from mysql.connector import Error
import json
import os
from my_logger import setup_logger
from hashlib import sha256
from datetime import date

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
            return True
        except Error as e:
            self.logger.error(f"Error executind adding new user. Query - {query}: {e}")
            return False
    
    def check_login_credentials(self, username: str, password_hash: str) -> bool:
        try:
            query = "SELECT COUNT(*) FROM users WHERE username = %s AND password = %s"
            results = self.execute_query(query, (username, password_hash))
            if results[0] == 1:
                self.logger.info(f"Login credentials for user {username} verified.")
                return True
            else:
                self.logger.info(f"Login credentials for user {username} not verified.")
                return False
        except Error as e:
            self.logger.error(f"Error executing login credentials check for user {username}: {e}")
            return False
    
    # create table for this function
    def add_auth_token(self, username: str) -> str:
        try:
            today_date = date.today().strftime('%Y-%m-%d')
            reference_string = username + today_date
            hashed_token = sha256(reference_string.encode()).hexdigest()
            query = "INSERT INTO auth_tokens VALUE %s"
            if self.execute_query(query, (hashed_token,)):
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
            query = "SELECT COUNT(*) FROM users WHERE username = %s"
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


    def execute_query(self, query, params=None):
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
            return results if results else True

        except mysql.connector.Error as error:
            self.logger.error(f"Error executing query: {error}")

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

    # query = "SELECT * FROM Users"
    username = 'suffaro'
    results = db.check_login_exists(username)
    db.test()
    print(results)

    db.close()



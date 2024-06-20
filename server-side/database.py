import pathlib
import mysql
import mysql.connector
from mysql.connector import Error
import json
from my_logger import setup_logger
from hashlib import sha256
from datetime import date, timedelta, datetime
import bcrypt
from random import randint
import os


class Database:
    def __init__(self, config_file) -> None:
        """
        Initialize the Database class.

        Args:
            config_file (str): The path to the JSON configuration file.

        This function initializes the Database class by loading the database configuration
        from a JSON file and setting up logging.
        """
        self.host = None
        self.user = None
        self.password = None
        self.database = None
        self.connection = None
        if not os.path.exists(os.path.join(os.path.dirname(__file__), "logs")):
            os.mkdir(os.path.join(os.path.dirname(__file__), "logs"))
        self.logger = setup_logger(logger_name="Database Logger", logger_file=os.path.join(os.path.dirname(__file__), "logs", "db_logs.log"))

        self.load_config(config_file)

    def load_config(self, config_file) -> None:
        """
        Load database configuration from a JSON file.

        Args:
            config_file (str): The path to the JSON configuration file.

        This function reads the database configuration from a JSON file and sets the
        'host', 'user', 'password', and 'database' attributes accordingly.
        """
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
        """
        Add a new user to the database.

        Args:
            username (str): The username of the new user.
            password_hash (str): The hashed password for the new user.

        Returns:
            bool: True if the new user was added successfully, False otherwise.

        This function adds a new user to the 'users' table in the database and creates a corresponding
        record in the 'Credits' table. It performs the following steps:

        1. Inserts a new row into the 'users' table with the provided username and password hash.
        2. Logs a message indicating the new user's login and password hash.
        3. Inserts a new row into the 'Credits' table with the new user's username.
        4. Logs a message indicating that a record was added to the credit system for the new user.
        5. Returns True if both insertions were successful, False otherwise.

        If an error occurs during the execution of the SQL queries, it logs an error message with
        the query and the error details, and returns False.
        """
        try:
            # Insert the new user into the 'users' table
            query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            self.execute_query(query, (username, password_hash))
            self.logger.info(f"Added new user with Login: {username} and Pass_Hash: {password_hash}")

            # Add a record for the new user in the 'Credits' table
            query = "INSERT INTO Credits(username) VALUES (%s)"
            self.execute_query(query, (username,))
            self.logger.info(f"Added record in credit system for user: {username}")

            return True

        except Error as e:
            self.logger.error(f"Error executing adding new user. Query - {query}: {e}")
            return False
    
    def get_models(self) -> list:
        """
        Retrieve a list of models from the database.

        Returns:
            list: A list of models retrieved from the database.

        This function retrieves a list of models from the 'models' table in the database
        and returns them as a list.
        """
        try:
            query = "SELECT * from models"
            models = self.execute_query(query)
            return models
        except Error as e:
            self.logger.error(f"Error executing get_models(). Query - {query}: {e}")
            return []

    def check_login_credentials(self, username: str, password: str) -> bool | str:
        """
        Check the login credentials of a user.

        Args:
            username (str): The username of the user.
            password (str): The password of the user.

        Returns:
            bool: True if the login credentials are valid, False otherwise.

        This function checks the provided username and password against the 'users'
        table in the database. It returns True if the credentials are valid, False
        otherwise.
        """
        try:
            query = "SELECT password FROM users WHERE username = %s"
            results = self.execute_query(query, (username,))
            
            if type(results) == list:
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
    
    def remove_auth_token(self, token: str) -> bool:
        """
        Remove an authentication token from the database.

        Args:
            token (str): The authentication token to remove.

        Returns:
            bool: True if the token was removed successfully, False otherwise.

        This function removes the specified authentication token from the 'auth_tokens'
        table in the database. It returns True if the token was removed successfully,
        False otherwise.
        """
        try:
            query = "DELETE FROM auth_tokens WHERE token = %s"
            if self.execute_query(query, (token,)):
                return True
            else:
                return False
        except Error as e:
            self.logger.error(f"Error executing remove_auth_token(): {e}")
            return False

    # create table for this function
    def add_auth_token(self, username: str, password: str) -> str:
        """
        Add an authentication token for a user.

        Args:
            username (str): The username of the user.
            password (str): The password of the user.

        Returns:
            str or None: The authentication token if added successfully, None otherwise.

        This function generates an authentication token for the user based on the
        provided username and password. It inserts the token into the 'auth_tokens'
        table in the database and returns the token if successful, None otherwise.
        """
        try:
            today_date = date.today().strftime('%Y-%m-%d')
            reference_string = username + password + today_date
            hashed_token = sha256(reference_string.encode()).hexdigest()
            query = "INSERT INTO auth_tokens (token, start_date, end_date, username) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE username=username"
            if self.execute_query(query, (hashed_token, today_date, (date.today() + timedelta(days=21)).strftime('%Y-%m-%d'), username)):
                return hashed_token
            else:
                return None
        except Error as e:
            self.logger.error(f"Something went wrong during add_auth_token function. Error - {e}")
        
    def verify_auth_token(self, token: str) -> bool:
        """
        Verify the authenticity of an authentication token.

        Args:
            token (str): The authentication token to verify.

        Returns:
            bool: True if the token is authentic, False otherwise.

        This function checks if the provided authentication token exists in the
        'auth_tokens' table in the database. It returns True if the token is found,
        indicating its authenticity, False otherwise.
        """
        try:
            query = "SELECT COUNT(*) FROM auth_tokens WHERE token = %s"
            results = self.execute_query(query, (token,))
            if results[0][0]:
                self.logger.info('verify_auth_token executed succesfully!')
                return True
            else: return False
        except Error as e:
            self.logger.error(f"Something went wrong during verify_auth_token function. Error - {e}")

    def check_login_exists(self, username: str) -> bool:
        """
        Check the login credentials of a user.

        Args:
            username (str): The username of the user.
            password (str): The password of the user.

        Returns:
            bool: True if the login credentials are valid, False otherwise.

        This function checks the provided username and password against the 'users'
        table in the database. It returns True if the credentials are valid, False
        otherwise.
        """
        try:
            query = "SELECT username FROM users WHERE username = %s"
            results = self.execute_query(query, (username,))
            if not results:
                self.logger.info('Check_login_exists executed succesfully!')
                return True
            else: 
                return False
        except Error as e:
            self.logger.error(f"Something went wrong during Check_login_exists function. Error - {e}")

    # i need subscription table for monitoring subscriptions of users
    # userid + subscription id + beginning date + cancelling date
    def add_user_premium_status(self, username: str, end_date: str) -> bool:
        try:
            query = "INSERT INTO Subscribers (username, end_date) VALUES (%s, %s)"
            results = self.execute_query(query, (username, end_date))
            self.logger.info('add_user_premium_status executed succesfully!')
            if results:
                return True
            else:
                return False
        except Error as e:
            self.logger.error(f"Something went wrong during add_user_premium_status function. Error - {e}")

    # for this i need to check monobank api
    def add_payment(self, username: str, payment_date: str, promotion_id: str) ->bool:
        try:
            query = "INSERT INTO add_payment (username, end_date, promotion_id) VALUES (%s, %s)"
            results = self.execute_query(query, (username, payment_date, promotion_id))
            self.logger.info('add_payment executed succesfully!')
            if results:
                return True
            else:
                return False
        except Error as e:
            self.logger.error(f"Something went wrong during add_payment function. Error - {e}")

    def delete_promotion(self, promotion_id) -> bool:
        try:
            query = "DELETE FROM promotions where promotion_id = %s"
            result = self.execute_query(query, (promotion_id, ))
            if result:
                self.logger.info('delete_promotion executed succesfully!')
                return True
            else:
                return False
        except Error as e:
            self.logger.error(f"Something went wrong during delete_promotion function. Error - {e}")

    def insert_promotion(self, subscription_length: str, cost: str, description: str) -> bool:
        try:
            query = "INSERT INTO promotions (subscription_length, cost, description) VALUES (%s, %s, %s)"
            result = self.execute_query(query, (subscription_length, cost, description))
            if result:
                self.logger.info('insert_promotion executed succesfully!')
                return True
            else:
                return False
        except Error as e:
            self.logger.error(f"Something went wrong during insert_promotion function. Error - {e}")


    def delete_user(self, username: str) -> bool:
        try:
            tables = ("auth_tokens", "confirmation_codes", "credits", "payments", "requests", "subscribers", "users")
            results = []
            for table in tables:
                query = f"DELETE FROM {table} where username = '{username}'"
                result = self.execute_query(query)
                results.append(result)
            if all(results):
                self.logger.info('delete_user executed succesfully!')
                return True
            else:
                return False
        except Error as e:
            self.logger.error(f"Something went wrong during delete_user function. Error - {e}")

    def delete_payment(self, payment_id: str) -> bool:
        try:
            query = "DELETE FROM payments where paymentID = %s"
            result = self.execute_query(query, (payment_id, ))
            if result:
                self.logger.info('delete_payment executed succesfully!')
                return True
            else:
                return False
        except Error as e:
            self.logger.error(f"Something went wrong during delete_payment function. Error - {e}")


    def add_request(self, username: str, requestText: str) -> bool:
        """
        Add a request to the database.

        Args:
            username (str): The username of the user making the request.
            requestText (str): The content of the request.

        Returns:
            bool: True if the request was added successfully, False otherwise.

        This function inserts a new request into the 'requests' table in the database
        with the provided username and request text. It returns True if the insertion was
        successful, False otherwise.
        """
        try:
            query = "INSERT INTO Requests (username, requestText) VALUES (%s, %s)"
            results = self.execute_query(query, (username, requestText))
            if results:
                self.logger.info('add_request executed succesfully!')
                return True
            else:
                return False
        except Error as e:
            self.logger.error(f"Something went wrong during add_request function. Error - {e}")

    def verify_premium_status(self, username: str) -> str | bool:
        """
        Verify the premium status of a user.

        Args:
            username (str): The username of the user.

        Returns:
            str or bool: The end date of the premium subscription if active, False otherwise.

        This function checks the premium status of the user specified by the username
        by querying the 'Subscribers' table in the database. If the user has an active
        premium subscription, it returns the end date of the subscription; otherwise, it
        returns False.
        """
        try:
            query = "SELECT end_date FROM Subscribers WHERE username = %s"
            results = self.execute_query(query, (username,))
            if results:
                self.logger.info('verify_premium_status executed succesfully!')
                return results[0][0]
            else: return False
        except Error as e:
            self.logger.error(f"Something went wrong during verify_premium_status function. Error - {e}")

    def get_subscriptions(self, locale) -> str:
        try:
            if locale == 'EN':
                query = "SELECT subscription_length, cost, description from promotions"
            else:
                query = "SELECT subscription_length_ua, cost, description_ua from promotions"
            results = self.execute_query(query, )
            if results:
                self.logger.info('get_subscription executed succesfully!')
                return results
            else: return False
        except Error as e:
            self.logger.error(f"Something went wrong during get_subscription function. Error - {e}")


    def reset_password(self, username: str, new_password: str) -> bool:
        try:
            query = "UPDATE Users SET password = %s WHERE username = %s"
            results = self.execute_query(query, (username, new_password))
            if results:
                self.logger.info('reset_password executed succesfully!')
                return results
            else: return False
        except Error as e:
            self.logger.error(f"Something went wrong during reset_password function. Error - {e}")

    def generate_confirmation_code(self, username: str) -> str:
        """
        Generate a confirmation code for a user.

        Args:
            username (str): The username of the user.

        Returns:
            str: The generated confirmation code.

        This function generates a confirmation code for the user specified by the username.
        It inserts the code into the 'confirmation_codes' table in the database and returns
        the generated code.
        """
        try:
            code = str(randint(100000, 999999))
            query = "INSERT INTO confirmation_codes(username, code, expiration_date) VALUES (%s, %s, %s)"
            expiration_date = datetime.now() + timedelta(minutes=10)
            results = self.execute_query(query, (username, code, expiration_date))
            if results:
                self.logger.info('generate_confirmation_code executed succesfully!')
                return code
            else: return False
        except Error as e:
            self.logger.error(f"Something went wrong during generate_confirmation_code function. Error - {e}")

    def verify_user_credits(self, username: str) -> str | bool:
        """
        Verify the credits balance of a user.

        Args:
            username (str): The username of the user.

        Returns:
            str or bool: The credits balance of the user, or False if an error occurs.

        This function checks the credits balance of the user specified by the username
        by querying the 'Credits' table in the database. It returns the credits balance
        if successful, or False if an error occurs.
        """
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
        """
        Decrement the credits balance of a user.

        Args:
            username (str): The username of the user.

        Returns:
            bool: True if the credits were decremented successfully, False otherwise.

        This function decrements the credits balance of the user specified by the username
        by updating the 'Credits' table in the database. It returns True if the operation
        was successful, False otherwise.
        """
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
        """
        Verify a confirmation code for a user.

        Args:
            username (str): The username of the user.
            code (str): The confirmation code to verify.

        Returns:
            bool: True if the confirmation code is valid for the user, False otherwise.

        This function verifies the provided confirmation code for the user specified by the
        username. It checks if the code exists in the 'confirmation_codes' table in the database
        for the given username and returns True if the code is valid, False otherwise.
        """
        try:
            query = "select code from confirmation_codes where username = %s and code = %s"
            results = self.execute_query(query, (username,code))
            if results:
                self.logger.info('verify_confirmation_code executed succesfully!')
                return True
            else: return False
        except Error as e:
            self.logger.error(f"Something went wrong during verify_confirmation_code function. Error - {e}")
    
    def delete_request(self, req_id: str) -> bool:
        try:
            query = "DELETE FROM requests where requestID = %s"
            result = self.execute_query(query, (req_id, ))
            if result:
                self.logger.info('delete_request executed succesfully!')
                return True
            else:
                return False
        except Error as e:
            self.logger.error(f"Something went wrong during delete_request function. Error - {e}")

    def delete_premium_status(self, username: str) -> bool:
        try:
            query = "delete from subscribers where username = %s"
            result = self.execute_query(query, (username, ))
            if result:
                self.logger.info('delete_premium_status executed succesfully!')
                return True
            else:
                return False
        except Error as e:
            self.logger.error(f"Something went wrong during delete_premium_status function. Error - {e}")

    def connect(self):
        """
        Connect to the MySQL database.

        This function establishes a connection to the MySQL database using the
        configured host, user, password, and database.
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=3306
            )
            if self.connection.is_connected():
                self.logger.info("Connected to MySQL database")
        except Error as e:
            self.logger.error(f"Error connecting to MySQL database: {e}")

    def close(self):
        """
        Close the connection to the MySQL database.

        This function closes the connection to the MySQL database if it is currently open.
        """
        if self.connection.is_connected():
            self.connection.close()
            self.logger.info("Connection to MySQL database closed")

    def execute_query(self, query, params=None) -> list | bool:
        """
        Execute a MySQL query and return the results.

        Args:
            query (str): The SQL query to execute.
            params (tuple, optional): A tuple of parameters to substitute into the query.

        Returns:
            list: A list of tuples containing the rows returned by the query.
            bool: True if the query executed successfully, False otherwise.

        This function executes the provided SQL query with optional parameters and returns
        the results as a list of tuples. It also logs any errors that occur during execution.
        """
       
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            self.connection.commit()
            if query[:6].lower() == "select":
                return results if results else False
            return results if results else True

        except mysql.connector.Error as error:
            self.logger.error(f"Error executing query: {error}")
            return False

        finally:
            cursor.close()





# Example usage:
if __name__ == "__main__":
    config_file = os.path.join(pathlib.Path(__file__).parent, 'config', 'db_config.json')
    db = Database(config_file)

    db.connect()

    # pass_hash = "$2b$12$N7hbRSm84721Lqslr29i.eEvqcxNA.WA6anBPNnniiNnnFYDD/KkO"

    # # query = "SELECT * FROM Users"
    username = 'rapperorwhat@gmail.com'
    password = "Suma1l24"
    # results = db.check_login_exists(username)

    # print(results)
    #db.get_models()

   # print(db.check_login_credentials(username, password))
    # print(db.check_login_credentials("seo23ij4", "sdfklj"))
    res = db.verify_confirmation_code("denpisotskiy@gmail.com", 396503)
    print(res)
    # print(db.check_login_credentials(username, pass_hash))

    #query = "select end_date from Subscribers"
    #db.execute_query(query, (username, ))

    # print(db.verify_premium_status(username))

    db.close()



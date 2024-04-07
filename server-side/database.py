import mysql.connector
import logging
from mysql.connector import Error

class Database:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    # add new user
    # check login credentials
    # add  auth_token
    # verify token
    # all payments
    # all users ??
    # all messages
    # add payment
    # add user premium status

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")

    def execute_query(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            # self.connection.commit()
            print("Query executed successfully")
            return cursor.fetchall()  # If the query is a SELECT statement
        except Error as e:
            print(f"Error executing query ({query}): {e}")

    def close(self):
        if self.connection.is_connected():
            self.connection.close()
            print("Connection to MySQL database closed")

# Example usage:
if __name__ == "__main__":
    db = Database(host="localhost", user="root", password="Suma1l24_", database="diploma_khai")

    db.connect()

    query = "SELECT * FROM Users"
    results = db.execute_query(query)
    print(results)



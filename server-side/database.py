import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

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
            self.connection.commit()
            print("Query executed successfully")
            return cursor.fetchall()  # If the query is a SELECT statement
        except Error as e:
            print(f"Error executing query: {e}")

    def close(self):
        if self.connection.is_connected():
            self.connection.close()
            print("Connection to MySQL database closed")

# Example usage:
if __name__ == "__main__":
    # Replace these with your actual MySQL database credentials
    db = Database(host="localhost", user="root", password="Suma1l24_", database="diploma_khai")

    db.connect()

    # Example query
    query = "SELECT * FROM USERS"
    results = db.execute_query(query)
    print(results)
    for row in results:
        print(row)

    db.close()

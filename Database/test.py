import psycopg2
from psycopg2 import Error

def connect_to_postgres(host, port, database, user, password):
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        print("Connected to PostgreSQL successfully")
        return connection
    except Error as e:
        print(f"Error while connecting to PostgreSQL: {e}")
        return None

def execute_select_query(connection, query):
    try:
        # Create a cursor object
        cursor = connection.cursor()

        # Execute the SELECT query
        cursor.execute(query)

        # Fetch all rows
        rows = cursor.fetchall()

        # Print the rows
        for row in rows:
            print(row)

        # Close the cursor
        cursor.close()
    except Error as e:
        print(f"Error executing SELECT query: {e}")

# Database connection parameters
host = "host.docker.internal"
port = "5432"
database = "naas"
user = "postgres"
password = "1234"

# Query to execute
query = "SELECT * FROM news_dawn"

# Connect to PostgreSQL
connection = connect_to_postgres(host, port, database, user, password)
if connection is not None:
    # Execute the SELECT query
    execute_select_query(connection, query)
    # Close the connection
    connection.close()

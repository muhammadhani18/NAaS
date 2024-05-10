import psycopg2
import sys
sys.path.append('/home/pcn/Desktop/NAaS/know')
from news_graph import NewsMining

# Initialize NewsMining
Miner = NewsMining()

# Database connection information
conn_params = {
    "host": "127.0.0.1",
    "database": "naas",
    "user": "postgres",
    "password": "1234"
}

# Connect to the PostgreSQL database
try:
    connection = psycopg2.connect(**conn_params)
    cursor = connection.cursor()

    # SQL query to fetch IDs from the table
    sql_query = "SELECT id, details FROM news_dawn;"

    # Execute the SQL query
    cursor.execute(sql_query)

    # Fetch all rows from the result
    rows = cursor.fetchall()
    rows=rows
    # print(rows)
    # cursor.execute("SELECT * from keywords;")
    # tables=cursor.fetchall()
    # print(tables)
    # # Process each row
    for row in rows:
        label_list = []
        label_id = row[0]
        details = row[1]

        # Obtain keywords using NewsMining
        try:
            data = Miner.main(details)
            # print(data)
            for label in data['edges']:
                label_list.append(label['label'])
        except Exception as err:
            pass
            # print(err)
                

    #     # Insert keywords and IDs into the "keywords" table
        for keyword in label_list:
            sql_insert = "INSERT INTO keywords (word, dawn_id) VALUES (%s,%s);"
            cursor.execute(sql_insert, (keyword, label_id))

    # # Commit the transaction
    connection.commit()
    # check_query="SELECT * from keywords;"
    # cursor.execute(check_query)
    # check_row=cursor.fetchall()
    # print(check_row)
    print("Keywords inserted successfully.")

except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL:", error)

finally:
    # Close the cursor and connection
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed.")

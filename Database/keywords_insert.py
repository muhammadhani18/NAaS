import psycopg2

# Connect to the PostgreSQL database
try:
    connection = psycopg2.connect(
        dbname="naas",
        user="postgres",
        password=1234,
        host="127.0.0.1",
        port=5432
    )
    cursor = connection.cursor()

    # SQL query to fetch dawn_id and word from keywords table and join with News_Dawn table
    query = """
        SELECT k.dawn_id, k.word
        FROM keywords AS k
        INNER JOIN News_Dawn AS d ON k.dawn_id = d.id;
    """

    # Execute the SQL query
    cursor.execute(query)

    # Fetch all rows and extract dawn_id and word into a list of tuples
    dawn_word_list = cursor.fetchall()

    # Print the dawn_id and word pairs
    # print(dawn_word_list)
    for dawn_id, word in dawn_word_list:
        # Update the News_Dawn table with the extracted word
        update_query = """
            UPDATE News_Dawn
            SET topics = array_append(topics, %s)
            WHERE id = %s;
        """
        cursor.execute(update_query, (word, dawn_id))
        connection.commit()

    print("Words inserted into the dawn topic field successfully.")


    query = """
        SELECT k.tribune_id, k.word
        FROM keywords AS k
        INNER JOIN News_Tribune AS d ON k.tribune_id = d.id;
    """

    # Execute the SQL query
    cursor.execute(query)


    dawn_word_list = cursor.fetchall()
    print(dawn_word_list)

    for dawn_id, word in dawn_word_list:
        # Update the News_Dawn table with the extracted word
        update_query = """
            UPDATE News_Tribune
            SET topics = array_append(topics, %s)
            WHERE id = %s;
        """
        cursor.execute(update_query, (word, dawn_id))
        connection.commit()

    print("Words inserted into the topic topic field successfully.")

    # Close cursor and connection
    cursor.close()
    connection.close()

except psycopg2.Error as e:
    print("Error connecting to PostgreSQL:", e)

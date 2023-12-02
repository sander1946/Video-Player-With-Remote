import sqlite3


try:
    connection = sqlite3.connect(f"databases/videos.db")
    with open(f"sql/videos.sql") as file:
        connection.executescript(file.read())
    connection.commit()
    connection.close()
    print(f"created database: database.db")
except sqlite3.Error as error:
    print(f"Error while creating a sqlite table: {error}")
finally:
    print("\nsqlite connection was successful")

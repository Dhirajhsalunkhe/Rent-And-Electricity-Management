import sqlite3

conn = sqlite3.connect("rent.db")

cursor = conn.cursor()

cursor.execute("SELECT * FROM rooms")

rooms = cursor.fetchall()

for room in rooms:
    print(room)

conn.close()
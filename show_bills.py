import sqlite3

conn = sqlite3.connect("rent.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM bills")

bills = cursor.fetchall()

for bill in bills:
    print(bill)

conn.close()
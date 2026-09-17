import sqlite3

conn = sqlite3.connect("rent.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS rooms(
id INTEGER PRIMARY KEY AUTOINCREMENT,
room_number TEXT,
rent INTEGER
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS tenant_history(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
room_number TEXT,
profession TEXT,
phone TEXT,
joining_date TEXT,
leaving_date TEXT,
rent INTEGER,
deposit INTEGER,
refund_amount INTEGER,
remarks TEXT
)
""")

cursor.execute("ALTER TABLE rooms ADD COLUMN phone TEXT")
cursor.execute("""
CREATE TABLE IF NOT EXISTS bills(
id INTEGER PRIMARY KEY AUTOINCREMENT,
room_id INTEGER,
prev_reading INTEGER,
curr_reading INTEGER,
units INTEGER,
electricity INTEGER,
water INTEGER,
balance INTEGER,
total INTEGER,
month TEXT
)
""")



rooms = [

("Room 1",3800,"9529298414"),
("Room 2",3700,"8605409645"),
("Room 3",4200,"7709995958"),
("Room 4",6500,"9834075770"),
("Room 5",7000,"7249740701"),
("Room 6",6000,"9632285380"),
("Room 7",6000,"8956215357"),
("Room 8",7000,"7972722366")
]


cursor.execute("DELETE FROM rooms")

for room in rooms:
    cursor.execute(
    "INSERT INTO rooms(room_number,rent,phone) VALUES(?,?,?)",
    room
    )

conn.commit()

print("Rooms with correct rent added")

conn.close()
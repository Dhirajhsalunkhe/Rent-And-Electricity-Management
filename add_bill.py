import sqlite3
from datetime import datetime

conn = sqlite3.connect("rent.db")
cursor = conn.cursor()

room_id = int(input("Enter Room ID (1-8): "))
curr = int(input("Enter Current Reading: "))
water = int(input("Water Charge: "))
balance = int(input("Previous Balance: "))

# get last reading
cursor.execute("SELECT curr_reading FROM bills WHERE room_id=? ORDER BY id DESC LIMIT 1",(room_id,))
last = cursor.fetchone()

prev = 0
if last:
    prev = last[0]

units = curr - prev
electricity = units * 12

cursor.execute("SELECT rent FROM rooms WHERE id=?",(room_id,))
rent = cursor.fetchone()[0]

total = rent + electricity + water + balance

month = datetime.now().strftime("%B %Y")

cursor.execute("""
INSERT INTO bills(room_id,prev_reading,curr_reading,units,electricity,water,balance,total,month)
VALUES(?,?,?,?,?,?,?,?,?)
""",(room_id,prev,curr,units,electricity,water,balance,total,month))

conn.commit()

print("Bill saved successfully")
print("Previous Reading:",prev)
print("Units Used:",units)
print("Electricity:",electricity)
print("Total Bill:",total)

conn.close()
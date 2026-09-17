import sqlite3

conn = sqlite3.connect("rent.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS settings(
    id INTEGER PRIMARY KEY,
    building_name TEXT,
    owner_name TEXT,
    owner_phone TEXT
)
""")

cursor.execute("""
INSERT OR IGNORE INTO settings
(id, building_name, owner_name, owner_phone)
VALUES
(1, 'Salunkhe Corner', 'Dhiraj Salunkhe', '9876543210')
""")

conn.commit()
conn.close()

print("Settings table created successfully.")
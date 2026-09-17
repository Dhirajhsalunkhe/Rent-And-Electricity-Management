import sqlite3
conn = sqlite3.connect("tenants.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tenants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    profession TEXT,
    joining_date TEXT,
    leaving_date TEXT,
    rent INTEGER NOT NULL,
    deposit INTEGER DEFAULT 0,
    status TEXT DEFAULT 'Occupied'
)
""")

conn.commit()
conn.close()

print("tenants.db created successfully!")
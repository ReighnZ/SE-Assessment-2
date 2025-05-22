import sqlite3

conn = sqlite3.connect('passwords.db')  # Ensure this is the correct DB file
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS passwords")
c.execute("""
    CREATE TABLE passwords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service TEXT,
        username TEXT,
        password TEXT,
        category TEXT,
        user_id INTEGER
    )
""")

conn.commit()
conn.close()
print("✅ passwords table recreated with category and user_id columns.")
import sqlite3

conn = sqlite3.connect('passwords.db')  # Make sure this path matches your project
c = conn.cursor()

c.execute("PRAGMA table_info(passwords);")
columns = c.fetchall()

print("✅ Columns in 'passwords' table:")
for col in columns:
    print(f"- {col[1]} ({col[2]})")

conn.close()
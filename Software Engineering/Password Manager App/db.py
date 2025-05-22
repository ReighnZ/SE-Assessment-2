import sqlite3

def init_db():
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS passwords (
        id INTEGER PRIMARY KEY,
        service TEXT,
        username TEXT,
        password TEXT)''')
    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect('passwords.db')
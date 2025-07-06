import sqlite3

def get_connection():
    conn = sqlite3.connect("database.db")
    return conn

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS licenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        license_key TEXT UNIQUE NOT NULL,
        expiry_date TEXT NOT NULL,
        is_active INTEGER DEFAULT 1
    )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()
    print("Database initialized ✅")

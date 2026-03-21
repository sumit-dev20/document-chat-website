import sqlite3

conn = sqlite3.connect("database/chat.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection_name TEXT,
    role TEXT,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
)

conn.commit()


def save_message(collection_name, role, content):
    cursor.execute(
        "INSERT INTO messages (collection_name, role, content) VALUES (?, ?, ?)",
        (collection_name, role, content),
    )
    conn.commit()


def load_chat(collection_name):
    cursor.execute(
        "SELECT role, content FROM messages WHERE collection_name = ? ORDER BY id ASC",
        (collection_name,),
    )
    rows = cursor.fetchall()

    return [{"role": r[0], "content": r[1]} for r in rows]


def delete_chat(collection_name):
    cursor.execute(
        "DELETE FROM messages WHERE collection_name = ?",
        (collection_name,),
    )
    conn.commit()

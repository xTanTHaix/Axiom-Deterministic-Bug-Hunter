"""
Sample Python file with SQL injection and hardcoded secret (for testing Layer 3)
"""

import sqlite3

API_SECRET_KEY = "AKIA1234567890EXAMPLE"


def get_user_by_name(username: str):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Dangerous: SQL injection via string formatting
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchall()


def delete_user(user_id: int):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Dangerous: Unparameterized DELETE query
    cursor.execute("DELETE FROM users WHERE id = %s" % user_id)
    conn.commit()

import sqlite3
from datetime import datetime, date

def init_db():
    conn = sqlite3.connect('dinner_poll.db')
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    # Submissions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            submission_date DATE,
            submitted BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, submission_date)
        )
    ''')

    # Insert sample users if empty
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        sample_users = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve']
        cursor.executemany('INSERT INTO users (name) VALUES (?)', [(name,) for name in sample_users])

    conn.commit()
    conn.close()

def get_users():
    conn = sqlite3.connect('dinner_poll.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM users ORDER BY name')
    users = cursor.fetchall()
    conn.close()
    return users

def get_user_submission_status(user_id, date_str):
    conn = sqlite3.connect('dinner_poll.db')
    cursor = conn.cursor()
    cursor.execute('SELECT submitted FROM submissions WHERE user_id = ? AND submission_date = ?', 
                   (user_id, date_str))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else False

def submit_poll(user_id, date_str):
    conn = sqlite3.connect('dinner_poll.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO submissions (user_id, submission_date, submitted)
        VALUES (?, ?, TRUE)
    ''', (user_id, date_str))
    conn.commit()
    conn.close()

def add_users_from_excel(df):
    conn = sqlite3.connect('dinner_poll.db')
    cursor = conn.cursor()
    for name in df.iloc[:, 0]:  # First column
        cursor.execute('INSERT OR IGNORE INTO users (name) VALUES (?)', (str(name).strip(),))
    conn.commit()
    conn.close()

def clear_old_submissions():
    conn = sqlite3.connect('dinner_poll.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM submissions WHERE submission_date < date("now", "-2 days")')
    conn.commit()
    conn.close()
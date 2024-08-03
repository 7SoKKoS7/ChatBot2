import sqlite3

# Создание и подключение к базе данных
conn = sqlite3.connect('chatbot.db')
cursor = conn.cursor()

# Создание таблиц
cursor.execute('''
CREATE TABLE IF NOT EXISTS sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time DATETIME,
    end_time DATETIME
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME,
    role TEXT,
    content TEXT,
    session_id INTEGER,
    is_important BOOLEAN,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME,
    event_type TEXT,
    description TEXT,
    session_id INTEGER,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS context (
    context_id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER,
    FOREIGN KEY (message_id) REFERENCES messages(message_id)
)
''')

conn.commit()
conn.close()

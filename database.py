import sqlite3
from datetime import date

DATABASE = 'guestbook.db'

def get_db_connection():
    """Устанавливает соединение с базой данных"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Создаёт таблицы messages и users, если их нет, и добавляет администратора"""
    conn = get_db_connection()
    
    # Таблица сообщений
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at DATE NOT NULL
        )
    ''')
    
    # Новая таблица пользователей
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    
    # Добавляем администратора, если его ещё нет
    conn.execute(
        'INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)',
        ('admin', '123')
    )
    
    conn.commit()
    conn.close()

def get_all_messages():
    """Возвращает все сообщения, отсортированные от новых к старым"""
    conn = get_db_connection()
    messages = conn.execute(
        'SELECT * FROM messages ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    return messages

def get_all_messages_sorted(order='DESC'):
    """
    Возвращает все сообщения с сортировкой.
    order = 'DESC' - сначала новые, 'ASC' - сначала старые
    """
    conn = get_db_connection()
    messages = conn.execute(
        f'SELECT * FROM messages ORDER BY created_at {order}'
    ).fetchall()
    conn.close()
    return messages

def add_message(name, message):
    """
    Добавляет новое сообщение в базу данных.
    Дата создания проставляется автоматически (текущая дата).
    """
    conn = get_db_connection()
    
    conn.execute(
        'INSERT INTO messages (name, message, created_at) VALUES (?, ?, ?)',
        (name, message, date.today().strftime('%Y-%m-%d'))
    )
    
    conn.commit()
    conn.close()

def delete_message(message_id):
    """Удаляет сообщение из базы данных по его id."""
    conn = get_db_connection()
    # Проверяем, что сообщение существует
    existing = conn.execute('SELECT * FROM messages WHERE id = ?', (message_id,)).fetchone()
    if existing:
        conn.execute('DELETE FROM messages WHERE id = ?', (message_id,))
        conn.commit()
        print(f"Сообщение {message_id} удалено")  # Для отладки
    else:
        print(f"Сообщение {message_id} не найдено")  # Для отладки
    conn.close()

def delete_all_messages():
    """Удаляет все сообщения из базы данных и сбрасывает счетчик id."""
    conn = get_db_connection()
    conn.execute('DELETE FROM messages')
    conn.execute("DELETE FROM sqlite_sequence WHERE name='messages'")
    conn.commit()
    conn.close()

def get_message_count():
    """Возвращает общее количество сообщений."""
    conn = get_db_connection()
    cursor = conn.execute('SELECT COUNT(*) FROM messages')
    count = cursor.fetchone()[0]
    conn.close()
    return count

def check_user(username, password):
    """
    Проверяет, существует ли пользователь с таким логином и паролем.
    Возвращает True, если пользователь найден, иначе False.
    """
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ? AND password = ?',
        (username, password)
    ).fetchone()
    conn.close()
    
    return user is not None
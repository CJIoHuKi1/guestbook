import pytest
import os
from app import app
from database import init_db, get_db_connection

@pytest.fixture
def client():
    """Фикстура для тестового клиента с чистой БД."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Создаем чистую БД для каждого теста
    init_db()
    
    with app.test_client() as client:
        yield client
    
    # После тестов очищаем БД
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM messages')
        conn.execute("DELETE FROM sqlite_sequence WHERE name='messages'")
        conn.execute('DELETE FROM users')
        conn.execute("DELETE FROM sqlite_sequence WHERE name='users'")
        conn.commit()
        conn.close()
    except:
        pass
    
    # Удаляем файл БД
    try:
        os.remove('guestbook.db')
    except:
        pass

@pytest.fixture
def auth_client(client):
    """Фикстура для авторизованного клиента."""
    # Входим
    client.post('/login', data={
        'username': 'admin',
        'password': '123'
    })
    return client
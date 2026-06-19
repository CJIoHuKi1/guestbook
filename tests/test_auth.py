from app import app
import pytest

# ============================================================
# ТЕСТ 1. Успешный вход
# ============================================================

def test_login_success(client):
    """Правильные логин и пароль должны установить сессию."""
    response = client.post('/login', data={
        'username': 'admin',
        'password': '123'
    })
    
    # Должен быть редирект на главную (код 302)
    assert response.status_code == 302
    
    # Проверяем, что сессия установлена
    with client.session_transaction() as sess:
        assert sess.get('logged_in') is True
        assert sess.get('username') == 'admin'


# ============================================================
# ТЕСТ 2. Неуспешный вход (неверный пароль)
# ============================================================

def test_login_failure(client):
    """Неверный пароль должен показать сообщение об ошибке."""
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'wrong'
    })
    
    # Страница с ошибкой (код 200, а не редирект 302)
    assert response.status_code == 200
    
    # Проверяем, что есть сообщение об ошибке
    assert 'Неверный логин или пароль'.encode('utf-8') in response.data
    
    # Проверяем, что сессия НЕ установлена
    with client.session_transaction() as sess:
        assert sess.get('logged_in') is None


# ============================================================
# ТЕСТ 3. Защита удаления (без авторизации)
# ============================================================

def test_delete_without_auth(client):
    """Неавторизованный пользователь не может удалять сообщения."""
    # Добавляем сообщение
    client.post('/add', data={
        'name': 'Тест',
        'message': 'Сообщение для удаления'
    })
    
    # Пробуем удалить без авторизации
    response = client.get('/delete/1')
    
    # Должен быть редирект на страницу входа
    assert response.status_code == 302
    
    # Проверяем, что сообщение осталось
    response = client.get('/')
    assert 'Сообщение для удаления'.encode('utf-8') in response.data


# ============================================================
# ТЕСТ 4. Удаление с авторизацией (ИСПРАВЛЕН)
# ============================================================

def test_delete_with_auth(client):
    """Авторизованный пользователь может удалять сообщения."""
    # Сначала входим
    client.post('/login', data={
        'username': 'admin',
        'password': '123'
    })
    
    # Добавляем сообщение
    client.post('/add', data={
        'name': 'Тест',
        'message': 'Сообщение для удаления'
    })
    
    # Проверяем, что сообщение появилось
    response = client.get('/')
    assert 'Сообщение для удаления'.encode('utf-8') in response.data
    
    # Получаем ID сообщения из базы данных
    from database import get_db_connection
    conn = get_db_connection()
    # Берем последнее добавленное сообщение
    message = conn.execute(
        'SELECT id FROM messages ORDER BY id DESC LIMIT 1'
    ).fetchone()
    conn.close()
    
    # Проверяем, что сообщение найдено
    assert message is not None, "Сообщение не найдено в БД"
    message_id = message['id']
    
    # Удаляем по реальному ID
    response = client.get(f'/delete/{message_id}')
    assert response.status_code == 302
    
    # Проверяем, что сообщение исчезло
    response = client.get('/')
    assert 'Сообщение для удаления'.encode('utf-8') not in response.data


# ============================================================
# ТЕСТ 5. Выход из системы
# ============================================================

def test_logout(client):
    """При выходе сессия должна очищаться."""
    # Сначала входим
    client.post('/login', data={
        'username': 'admin',
        'password': '123'
    })
    
    # Проверяем, что вошли
    with client.session_transaction() as sess:
        assert sess.get('logged_in') is True
    
    # Выходим
    client.get('/logout')
    
    # Проверяем, что вышли
    with client.session_transaction() as sess:
        assert sess.get('logged_in') is None
        assert sess.get('username') is None
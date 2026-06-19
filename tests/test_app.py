from app import app
import pytest

def test_index(client):
    """Главная страница должна открываться."""
    response = client.get('/')
    assert response.status_code == 200
    assert 'Гостевая книга'.encode('utf-8') in response.data

def test_add_message(client):
    """После отправки формы сообщение должно появиться."""
    # Отправляем форму
    client.post('/add', data={
        'name': 'Тест',
        'message': 'Привет!'
    })
    
    # Проверяем, что сообщение появилось на главной
    response = client.get('/')
    assert 'Тест'.encode('utf-8') in response.data
    assert 'Привет!'.encode('utf-8') in response.data

def test_login_page(client):
    """Страница входа должна содержать форму."""
    response = client.get('/login')
    assert response.status_code == 200
    assert 'Вход'.encode('utf-8') in response.data
    assert 'username'.encode('utf-8') in response.data
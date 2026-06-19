from flask import Flask, render_template, request, redirect, session
from database import (
    init_db, get_all_messages, get_all_messages_sorted, 
    add_message, delete_message, delete_all_messages, get_message_count, check_user
)
from filters import format_date_russian
from datetime import date

app = Flask(__name__)

# Секретный ключ нужен для шифрования данных сессии
app.secret_key = 'секретный_ключ_для_гостевой_книги_12345'

# Добавляем фильтр для русских дат
app.jinja_env.filters['date_russian'] = format_date_russian

# Инициализируем базу данных (создаёт таблицы и администратора)
init_db()

@app.route('/')
def index():
    """Главная страница: показывает все сообщения (сначала новые)."""
    messages = get_all_messages()
    total_count = get_message_count()
    today = date.today().isoformat()
    
    # Передаём в шаблон информацию об авторизации
    return render_template(
        'index.html',
        messages=messages,
        total_count=total_count,
        today=today,
        logged_in=session.get('logged_in', False),
        username=session.get('username')
    )

@app.route('/add', methods=['POST'])
def add():
    """Обрабатывает отправку нового сообщения."""
    name = request.form.get('name', '').strip()
    message = request.form.get('message', '').strip()
    
    if name and message:
        add_message(name, message)
        session['success'] = True
        return redirect('/')
    else:
        messages = get_all_messages()
        total_count = get_message_count()
        today = date.today().isoformat()
        error = '⚠️ Заполните все поля!'
        return render_template('index.html', messages=messages, total_count=total_count, 
                             today=today, error=error, logged_in=session.get('logged_in', False),
                             username=session.get('username'))

@app.route('/delete/<int:message_id>')
def delete(message_id):
    """
    Удаляет сообщение по id.
    Только авторизованный пользователь может удалять.
    """
    # Проверяем, авторизован ли пользователь
    if not session.get('logged_in'):
        return redirect('/login')
    
    delete_message(message_id)
    session['deleted'] = True
    return redirect('/')

# Сортировка по дате
@app.route('/sort/newest')
def sort_newest():
    """Сортировка: сначала новые сообщения."""
    messages = get_all_messages_sorted('DESC')
    total_count = get_message_count()
    today = date.today().isoformat()
    return render_template('index.html', messages=messages, total_count=total_count, 
                         today=today, logged_in=session.get('logged_in', False),
                         username=session.get('username'))

@app.route('/sort/oldest')
def sort_oldest():
    """Сортировка: сначала старые сообщения."""
    messages = get_all_messages_sorted('ASC')
    total_count = get_message_count()
    today = date.today().isoformat()
    return render_template('index.html', messages=messages, total_count=total_count, 
                         today=today, logged_in=session.get('logged_in', False),
                         username=session.get('username'))

# Удаление всех сообщений
@app.route('/delete-all')
def delete_all_page():
    """Страница подтверждения удаления всех сообщений."""
    if not session.get('logged_in'):
        return redirect('/login')
    
    total_count = get_message_count()
    return render_template('delete_all.html', total_count=total_count)

@app.route('/delete-all-confirm', methods=['POST'])
def delete_all_confirm():
    """Подтверждение удаления всех сообщений."""
    if not session.get('logged_in'):
        return redirect('/login')
    
    delete_all_messages()
    session['all_deleted'] = True
    return redirect('/')

# ========== НОВЫЕ МАРШРУТЫ ДЛЯ АВТОРИЗАЦИИ ==========

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Страница входа в приложение.
    GET — показывает форму входа.
    POST — обрабатывает отправленные логин и пароль.
    """
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Проверяем логин и пароль
        if check_user(username, password):
            # Сохраняем информацию о входе в сессию
            session['logged_in'] = True
            session['username'] = username
            return redirect('/')
        else:
            error = '❌ Неверный логин или пароль'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    """
    Выход из приложения.
    Удаляет данные пользователя из сессии.
    """
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=5002)
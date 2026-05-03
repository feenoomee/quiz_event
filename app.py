from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from functools import wraps
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Mock User Object (Replace with real User model)
class User:
    def __init__(self, id, username, email, is_admin=False):
        self.id = id
        self.username = username
        self.email = email
        self.is_admin = is_admin
        self.is_authenticated = True

    def is_active(self):
        return True

# Mock current_user
class CurrentUser:
    def __init__(self):
        self.is_authenticated = False
        self.username = None
        self.is_admin = False

current_user = CurrentUser()

# Helper: Check if user is authenticated
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Helper: Check if user is admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ===== ROUTES =====

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html', current_user=current_user)

@app.route('/schedule')
def schedule():
    """Страница расписания мероприятий"""
    return render_template('schedule.html', current_user=current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    if request.method == 'POST':
        # Обработка регистрации
        data = request.get_json() if request.is_json else request.form
        # Здесь будет логика регистрации
        return jsonify({'success': True, 'message': 'Регистрация успешна'})
    return render_template('register.html', current_user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Здесь будет логика входа
        # Для демонстрации просто устанавливаем текущего пользователя
        current_user.is_authenticated = True
        current_user.username = username
        current_user.is_admin = username == 'admin'  # Simple admin check
        return redirect(url_for('profile'))
    return render_template('login.html', current_user=current_user)

@app.route('/logout')
def logout():
    """Выход из аккаунта"""
    current_user.is_authenticated = False
    current_user.username = None
    current_user.is_admin = False
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    """Профиль пользователя"""
    return render_template('profile.html', current_user=current_user)

@app.route('/chat')
@login_required
def chat():
    """Чат"""
    return render_template('chat.html', current_user=current_user)

@app.route('/admin')
@admin_required
def admin():
    """Админ-панель"""
    return render_template('admin.html', current_user=current_user)

# ===== API ENDPOINTS =====

@app.route('/api/events', methods=['GET', 'POST'])
def api_events():
    """API для получения и создания событий"""
    if request.method == 'GET':
        # Mock data
        events = [
            {'id': 1, 'title': 'Квиз «Кино»', 'date': '2026-05-15', 'seats': 10, 'available': 8},
            {'id': 2, 'title': 'Квиз «История»', 'date': '2026-05-22', 'seats': 20, 'available': 5},
        ]
        return jsonify(events)
    elif request.method == 'POST':
        data = request.get_json()
        # Здесь будет логика создания события
        return jsonify({'success': True, 'id': 3})

@app.route('/api/events/<int:event_id>', methods=['GET', 'PUT', 'DELETE'])
@admin_required
def api_event_detail(event_id):
    """API для конкретного события"""
    if request.method == 'GET':
        return jsonify({'id': event_id, 'title': 'Квиз', 'date': '2026-05-15'})
    elif request.method == 'PUT':
        data = request.get_json()
        return jsonify({'success': True})
    elif request.method == 'DELETE':
        return jsonify({'success': True})

@app.route('/api/registrations', methods=['POST'])
def api_registrations():
    """API для регистрации на событие"""
    data = request.get_json()
    # Здесь будет логика регистрации
    return jsonify({'success': True, 'message': 'Регистрация успешна'})

@app.route('/api/analytics', methods=['GET'])
@admin_required
def api_analytics():
    """API для получения аналитики"""
    # Mock analytics data
    analytics = {
        'total_events': 24,
        'total_participants': 487,
        'total_revenue': 487000,
        'upcoming_events': 5,
        'period_events': 8,
        'period_participants': 156,
        'period_revenue': 78500,
        'average_occupancy': 78,
    }
    return jsonify(analytics)

@app.route('/api/chat/messages', methods=['GET', 'POST'])
@login_required
def api_chat_messages():
    """API для получения и отправки сообщений"""
    if request.method == 'GET':
        # Mock messages
        messages = [
            {'id': 1, 'user': 'Мария', 'text': 'Привет!', 'timestamp': '12:45'},
            {'id': 2, 'user': 'Ты', 'text': 'Привет!', 'timestamp': '12:46'},
        ]
        return jsonify(messages)
    elif request.method == 'POST':
        data = request.get_json()
        # Здесь будет логика отправки сообщения
        return jsonify({'success': True, 'id': 3})

# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    """Обработчик ошибки 404"""
    return render_template('index.html', current_user=current_user), 404

@app.errorhandler(500)
def internal_error(error):
    """Обработчик ошибки 500"""
    return render_template('index.html', current_user=current_user), 500

# ===== CONTEXT PROCESSORS =====

@app.context_processor
def inject_current_user():
    """Добавить current_user в контекст шаблонов"""
    return dict(current_user=current_user)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

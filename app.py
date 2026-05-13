from flask import Flask, render_template, send_from_directory, jsonify, session, request, redirect, url_for
import os

app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')
app.secret_key = 'your-secret-key-here'

# Simulated database of users with roles
users = {
    'user123': {'name': 'Иван Петров', 'role': 'user', 'email': 'ivan@example.com'},
    'admin123': {'name': 'Администратор', 'role': 'admin', 'email': 'admin@example.com'}
}

# Simulated events data
events = {
    1: {'title': 'Кино и сериалы 2025', 'date': '2026-06-13', 'time': '19:00', 'location': 'ТЦ Ёлки', 'max_seats': 30, 'registered': 24, 'price': 600},
    2: {'title': 'Угадай мелодию', 'date': '2026-06-20', 'time': '20:00', 'location': 'ТЦ Ёлки', 'max_seats': 25, 'registered': 18, 'price': 550},
    3: {'title': 'История и культура', 'date': '2026-06-27', 'time': '19:00', 'location': 'Клуб 360', 'max_seats': 35, 'registered': 32, 'price': 650},
}

@app.route('/')
def index():
    """Render the main landing page"""
    return render_template('index.html')


def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    user = users.get(user_id)
    if not user:
        session.pop('user_id', None)
        return None
    return {'id': user_id, **user}


@app.context_processor
def inject_current_user():
    return {'current_user': get_current_user()}

@app.route('/media/<filename>')
def serve_media(filename):
    """Serve files from media folder"""
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'media'), filename)

@app.route('/api/register', methods=['POST'])
def register_team():
    """Handle team registration (placeholder)"""
    # This is where you'll handle the registration logic
    # For now, it's a placeholder
    return {'status': 'success', 'message': 'Registration received'}

@app.route('/profile')
def profile():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for('index'))
    if current_user['role'] == 'admin':
        return redirect(url_for('admin'))
    return render_template('profile.html', current_user=current_user)

@app.route('/admin')
def admin():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for('index'))
    if current_user['role'] != 'admin':
        return redirect(url_for('profile'))
    return render_template('admin.html', current_user=current_user)


@app.route('/dashboard')
def dashboard():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for('index'))
    if current_user['role'] == 'admin':
        return redirect(url_for('admin'))
    return redirect(url_for('profile'))


@app.route('/api/login', methods=['POST'])
def login():
    payload = request.get_json(silent=True) or {}
    identifier = (payload.get('identifier') or '').strip().lower()
    if not identifier:
        return jsonify({'status': 'error', 'message': 'Укажите логин или email'}), 400

    matched_user_id = None
    for user_id, user in users.items():
        if user_id.lower() == identifier or user['email'].lower() == identifier:
            matched_user_id = user_id
            break

    if not matched_user_id:
        return jsonify({'status': 'error', 'message': 'Пользователь не найден'}), 401

    session['user_id'] = matched_user_id
    destination = url_for('admin') if users[matched_user_id]['role'] == 'admin' else url_for('profile')
    return jsonify({'status': 'success', 'redirect_to': destination})


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/stats')
def get_stats():
    """Get statistics data for admin panel"""
    # Generate sample data for last 30 days
    stats = {
        'total_events': len(events),
        'total_revenue': sum(e['registered'] * e['price'] for e in events.values()),
        'total_attendees': sum(e['registered'] for e in events.values()),
        'occupancy_rate': round(sum(e['registered'] for e in events.values()) / sum(e['max_seats'] for e in events.values()) * 100, 1),
        'events': events,
        'attendance_data': {
            'labels': ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
            'values': [120, 150, 180, 200, 220, 250, 180]
        },
        'revenue_data': {
            'labels': ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
            'values': [72000, 90000, 108000, 120000, 132000, 150000, 108000]
        },
        'top_events': sorted(events.values(), key=lambda x: x['registered'], reverse=True)[:3],
        'event_distribution': {
            'labels': ['Кино', 'Музыка', 'История', 'Другое'],
            'values': [30, 25, 20, 15]
        }
    }
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True)

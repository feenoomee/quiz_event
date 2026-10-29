from datetime import datetime, timedelta, timezone

from flask import g

import pytest

from quiz_app.models import ChatMessage, User


def token(client):
    # conftest keeps one app context open across requests from different clients.
    g.pop('_login_user', None)
    g.pop('csrf_token', None)
    return client.get('/api/chat/messages').get_json()['csrf_token']


def send(client, text, **extra):
    return client.post('/api/chat/messages', json={'text': text, **extra},
                       headers={'X-CSRFToken': token(client)})


def test_guests_can_read_but_cannot_post(client):
    response = client.get('/api/chat/messages')
    assert response.status_code == 200
    assert response.get_json()['messages'] == []
    assert response.headers['Cache-Control'] == 'no-store'
    assert send(client, 'Hello').status_code == 401


def test_shared_messages_and_author_identity(user, admin_client, db):
    author = User.query.filter_by(email='test@example.com').one()
    author.avatar = 'uploads/avatars/player.webp'
    db.session.commit()
    response = send(user, '  Привет, игроки!  ', user_id=999, is_admin=True)
    assert response.status_code == 201
    message = response.get_json()['message']
    assert message['text'] == 'Привет, игроки!'
    assert message['user'] == {
        'id': author.id, 'name': 'Test User',
        'avatar': '/media/uploads/avatars/player.webp', 'is_admin': False,
    }
    assert message['created_at'].endswith('Z')
    assert send(admin_client, 'Добро пожаловать!').get_json()['message']['user']['is_admin']
    rows = admin_client.get('/api/chat/messages').get_json()['messages']
    assert [row['text'] for row in rows] == ['Привет, игроки!', 'Добро пожаловать!']
    assert ChatMessage.query.count() == 2
    assert not ({'email', 'phone', 'password_hash'} & rows[0]['user'].keys())


@pytest.mark.parametrize('value', ['', '   ', 'x' * 2001, None, 1, [], {}])
def test_invalid_message(user, value):
    assert send(user, value).status_code == 400
    assert ChatMessage.query.count() == 0


def test_csrf_and_throttle(user):
    assert user.post('/api/chat/messages', json={'text': 'No token'}).status_code == 400
    assert send(user, 'First').status_code == 201
    assert send(user, 'Too soon').status_code == 429
    assert ChatMessage.query.count() == 1


def test_history_and_incremental_updates(user, db):
    author = User.query.filter_by(email='test@example.com').one()
    for index in range(125):
        db.session.add(ChatMessage(user_id=author.id, text=str(index),
                                   created_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=1)))
    db.session.commit()
    latest = user.get('/api/chat/messages').get_json()
    assert len(latest['messages']) == 50
    assert latest['has_more']
    assert latest['messages'][0]['text'] == '75'
    before = latest['messages'][0]['id']
    older = user.get(f'/api/chat/messages?before={before}').get_json()
    assert [row['text'] for row in older['messages']] == [str(i) for i in range(25, 75)]
    after = user.get('/api/chat/messages?after=0').get_json()
    assert [row['text'] for row in after['messages']] == [str(i) for i in range(50)]
    assert after['has_more']
    last_id = latest['messages'][-1]['id']
    assert send(user, '<script>alert(1)</script>').status_code == 201
    new = user.get(f'/api/chat/messages?after={last_id}').get_json()
    assert len(new['messages']) == 1
    assert new['messages'][0]['text'] == '<script>alert(1)</script>'
    assert not new['has_more']


@pytest.mark.parametrize('query', ['after=bad', 'before=-1', 'after=1&before=2', 'after=999999999999999999999'])
def test_invalid_cursor(client, query):
    assert client.get('/api/chat/messages?' + query).status_code == 400


def test_chat_on_all_pages(user, admin_client):
    for client, path in [(user, '/'), (user, '/profile'), (admin_client, '/admin'), (user, '/chat')]:
        g.pop('_login_user', None)
        response = client.get(path)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert html.count('data-game-chat ') == 1
        assert 'css/chat.css' in html and 'js/chat.js' in html
        assert ('data-chat-toggle' in html) == (path != '/chat')
        assert 'Ваше сообщение' in html


def test_guest_chat_page(client):
    html = client.get('/chat').get_data(as_text=True)
    assert 'Войдите или зарегистрируйтесь' in html
    assert 'data-chat-form' not in html

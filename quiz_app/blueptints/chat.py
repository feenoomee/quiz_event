from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request, url_for
from flask_login import current_user
from flask_wtf.csrf import generate_csrf, validate_csrf
from wtforms.validators import ValidationError

from quiz_app import db
from quiz_app.models import ChatMessage

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")
PAGE_SIZE = 50


def message_payload(message):
    user = message.user
    return {
        "id": message.id,
        "text": message.text,
        "created_at": message.created_at.isoformat(timespec="seconds") + "Z",
        "user": {
            "id": user.id,
            "name": user.name,
            "avatar": url_for("pages.serve_media", filename=user.avatar) if user.avatar else None,
            "is_admin": user.role == "admin",
        },
    }


@chat_bp.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store"
    return response


@chat_bp.get("/messages")
def messages():
    cursors = {}
    for key in ("after", "before"):
        raw = request.args.get(key)
        if raw is not None:
            try:
                cursors[key] = int(raw)
                if not 0 <= cursors[key] <= 9223372036854775807:
                    raise ValueError
            except ValueError:
                return jsonify(message="Некорректный номер сообщения"), 400
    if len(cursors) > 1:
        return jsonify(message="Укажите только одно направление загрузки"), 400

    query = ChatMessage.query
    if "after" in cursors:
        query = query.filter(ChatMessage.id > cursors["after"]).order_by(ChatMessage.id.asc())
    else:
        if "before" in cursors:
            query = query.filter(ChatMessage.id < cursors["before"])
        query = query.order_by(ChatMessage.id.desc())
    rows = query.limit(PAGE_SIZE + 1).all()
    has_more = len(rows) > PAGE_SIZE
    rows = rows[:PAGE_SIZE]
    if "after" not in cursors:
        rows.reverse()
    return jsonify(
        messages=[message_payload(row) for row in rows],
        has_more=has_more,
        csrf_token=generate_csrf(),
    )


@chat_bp.post("/messages")
def send_message():
    if not current_user.is_authenticated:
        return jsonify(message="Войдите на сайт, чтобы написать в чат"), 401
    try:
        validate_csrf(request.headers.get("X-CSRFToken"))
    except ValidationError:
        return jsonify(message="Обновите страницу и повторите отправку"), 400
    data = request.get_json(silent=True)
    text = data.get("text") if isinstance(data, dict) else None
    if not isinstance(text, str) or not text.strip():
        return jsonify(message="Введите сообщение"), 400
    text = text.strip()
    if len(text) > 2000:
        return jsonify(message="Сообщение должно быть не длиннее 2000 символов"), 400
    recent = ChatMessage.query.filter(
        ChatMessage.user_id == current_user.id,
        ChatMessage.created_at > datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=2),
    ).first()
    if recent:
        return jsonify(message="Подождите пару секунд перед следующим сообщением"), 429
    message = ChatMessage(user_id=current_user.id, text=text)
    db.session.add(message)
    db.session.commit()
    return jsonify(message=message_payload(message)), 201

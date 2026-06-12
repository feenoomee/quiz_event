import os
import uuid
from datetime import datetime

from flask import Blueprint, jsonify, request, url_for, current_app
from flask_login import login_required, current_user, login_user
from werkzeug.utils import secure_filename

from quiz_app import db
from quiz_app.models import User, Event
from ..helpers import _format_short_name, _require_admin_json, _MONTHS_RU

api_bp = Blueprint("api", __name__, url_prefix="/api")

scoreboards = {}
SCOREBOARD_ROUNDS = 7

_WEEKDAYS_RU = [
    "понедельник", "вторник", "среда", "четверг",
    "пятница", "суббота", "воскресенье",
]


def _format_event(event):
    d = event.date or datetime.now()
    photo_url = url_for("pages.serve_media", filename=event.photo) if event.photo else None
    return {
        "id": event.id,
        "title": event.name,
        "description": event.description,
        "category": event.category,
        "date": f"{d.day} {_MONTHS_RU[d.month]}, {_WEEKDAYS_RU[d.weekday()]}",
        "time": d.strftime("%H:%M"),
        "place": event.location,
        "price": event.price,
        "total": event.seats,
        "booked": event.booked,
        "tag": event.tag or "",
        "photo": photo_url,
    }


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config.get("ALLOWED_EXTENSIONS", set())

def _save_upload(file, subfolder):
    if not file or not _allowed_file(file.filename):
        return None
    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    folder = os.path.join(current_app.config["UPLOAD_FOLDER"], subfolder)
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, unique_name))
    return f"uploads/{subfolder}/{unique_name}"


@api_bp.route("/upload/avatar", methods=["POST"])
@login_required
def upload_avatar():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "Файл не передан"}), 400
    file = request.files["file"]
    rel_path = _save_upload(file, "avatars")
    if not rel_path:
        return jsonify({"status": "error", "message": "Недопустимый формат файла"}), 400
    current_user.avatar = rel_path
    try:
        db.session.commit()
        photo_url = url_for("pages.serve_media", filename=rel_path)
        return jsonify({"status": "success", "url": photo_url})
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Не удалось сохранить"}), 500


@api_bp.route("/upload/event-photo", methods=["POST"])
@login_required
def upload_event_photo():
    if not _require_admin_json():
        return jsonify({"status": "error", "message": "Нет доступа"}), 403
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "Файл не передан"}), 400
    file = request.files["file"]
    rel_path = _save_upload(file, "events")
    if not rel_path:
        return jsonify({"status": "error", "message": "Недопустимый формат файла"}), 400
    photo_url = url_for("pages.serve_media", filename=rel_path)
    return jsonify({"status": "success", "url": photo_url, "path": rel_path})


# Events CRUD
@api_bp.route("/events", methods=["GET"])
def list_events():
    events = Event.query.order_by(Event.date).all()
    return jsonify([_format_event(e) for e in events])


@api_bp.route("/events", methods=["POST"])
def create_event():
    if not _require_admin_json():
        return jsonify({"status": "error", "message": "Нет доступа"}), 403
    data = request.get_json(silent=True) or {}

    name = (data.get("title") or "").strip()
    category = (data.get("category") or "").strip()
    date_str = (data.get("date") or "").strip()
    time_str = (data.get("time") or "").strip()
    location = (data.get("location") or "").strip()
    description = (data.get("description") or "").strip()

    try:
        price = int(data.get("price", 0))
    except (TypeError, ValueError):
        price = 0
    try:
        seats = int(data.get("seats") or data.get("max_seats", 0))
    except (TypeError, ValueError):
        seats = 0
    tag = (data.get("tag") or "").strip()

    if not all([name, category, date_str, time_str, location]):
        return jsonify({"status": "error", "message": "Заполните обязательные поля"}), 400

    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        t = datetime.strptime(time_str, "%H:%M").time()
        event_date = datetime.combine(d, t)
    except ValueError:
        return jsonify({"status": "error", "message": "Неверный формат даты или времени"}), 400

    photo_path = (data.get("photo_path") or "").strip()

    event = Event(
        name=name,
        description=description or name,
        category=category,
        date=event_date,
        time=event_date,
        location=location,
        seats=seats,
        price=price,
        tag=tag,
        photo=photo_path or None,
    )

    try:
        db.session.add(event)
        db.session.commit()
        return jsonify({"status": "success", "event": _format_event(event)}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Не удалось создать мероприятие"}), 500


@api_bp.route("/events/<int:event_id>", methods=["PUT"])
def update_event(event_id):
    if not _require_admin_json():
        return jsonify({"status": "error", "message": "Нет доступа"}), 403

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"status": "error", "message": "Мероприятие не найдено"}), 404

    data = request.get_json(silent=True) or {}

    if "title" in data:
        event.name = data["title"].strip() or event.name
    if "category" in data:
        event.category = data["category"].strip() or event.category
    if "location" in data:
        event.location = data["location"].strip() or event.location
    if "description" in data:
        event.description = data["description"].strip() or event.description
    if "tag" in data:
        event.tag = data["tag"].strip()
    if "photo_path" in data:
        val = (data["photo_path"] or "").strip()
        event.photo = val or None
    if "price" in data:
        try:
            event.price = int(data["price"])
        except (TypeError, ValueError):
            pass
    if "seats" in data or "max_seats" in data:
        try:
            event.seats = int(data.get("seats") or data.get("max_seats", event.seats))
        except (TypeError, ValueError):
            pass

    date_str = data.get("date")
    time_str = data.get("time")
    if date_str and time_str:
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
            t = datetime.strptime(time_str, "%H:%M").time()
            event.date = datetime.combine(d, t)
            event.time = event.date
        except ValueError:
            pass

    try:
        db.session.commit()
        return jsonify({"status": "success", "event": _format_event(event)})
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Не удалось обновить"}), 500


@api_bp.route("/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    if not _require_admin_json():
        return jsonify({"status": "error", "message": "Нет доступа"}), 403

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"status": "error", "message": "Мероприятие не найдено"}), 404

    try:
        db.session.delete(event)
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Не удалось удалить"}), 500


# Регистрация на ивент
@api_bp.route("/register_team", methods=["POST"])
def register_team():
    if not current_user.is_authenticated:
        return jsonify({"status": "error", "message": "Войдите в аккаунт"}), 401
    return {"status": "success", "message": "Registration received"}


# Вход
@api_bp.route("/login", methods=["POST"])
def login_account():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or payload.get("identifier") or "").strip().lower()
    password = payload.get("password") or ""
    if not email or not password:
        return jsonify({"status": "error", "message": "Укажите email и пароль"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"status": "error", "message": "Неверный email или пароль"}), 401

    login_user(user)
    return jsonify(
        {
            "status": "success",
            "redirect_to": url_for("pages.index"),
            "user": {
                "id": user.id,
                "name": user.name,
                "short_name": _format_short_name(user.name),
                "role": user.role,
            },
        }
    )


# Регистрация аккаунта


@api_bp.route("/signup", methods=["POST"])
def signup():
    payload = request.get_json(silent=True) or {}
    first_name = (payload.get("first_name") or "").strip()
    second_name = (payload.get("second_name") or "").strip()
    phone = (payload.get("phone") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not all([first_name, second_name, phone, email, password]):
        return jsonify({"status": "error", "message": "Заполните все поля регистрации"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"status": "error", "message": "Пользователь с таким email уже существует"}), 409

    user = User(
        first_name=first_name,
        second_name=second_name,
        email=email,
        role="user",
        number_telephone=phone,
    )
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Не удалось создать аккаунт"}), 500

    login_user(user)
    return jsonify(
        {
            "status": "success",
            "redirect_to": url_for("pages.index"),
            "user": {
                "id": user.id,
                "name": user.name,
                "short_name": _format_short_name(user.name),
                "role": user.role,
            },
        }
    ), 201


# Обновление профиля


@api_bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    payload = request.get_json(silent=True) or {}
    first_name = (payload.get("first_name") or "").strip()
    second_name = (payload.get("second_name") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    phone = (payload.get("phone") or "").strip()

    if not all([first_name, second_name, email]):
        return jsonify({"status": "error", "message": "Имя, фамилия и email обязательны"}), 400

    if email != current_user.email:
        existing = User.query.filter_by(email=email).first()
        if existing:
            return jsonify({"status": "error", "message": "Этот email уже занят"}), 409

    current_user.first_name = first_name
    current_user.second_name = second_name
    current_user.email = email
    if phone:
        current_user.number_telephone = phone

    try:
        db.session.commit()
        return jsonify({"status": "success", "message": "Профиль обновлён"})
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Не удалось сохранить"}), 500


#dmin: недавние игры
@api_bp.route("/admin/recent-games")
def admin_recent_games():
    if not _require_admin_json():
        return jsonify({"status": "error", "message": "Нет доступа"}), 403
    limit = request.args.get("limit", default=15, type=int) or 15
    limit = max(1, min(limit, 50))
    events = Event.query.order_by(Event.date.desc()).limit(limit).all()
    rows = []
    for e in events:
        d = e.date
        rows.append(
            {
                "id": e.id,
                "title": e.name,
                "date": f"{d.day} {_MONTHS_RU[d.month]} {d.year}",
                "time": d.strftime("%H:%M"),
                "location": e.location,
            }
        )
    return jsonify({"games": rows})


#Admin: таблица результатов
@api_bp.route("/admin/games/<int:event_id>/scoreboard", methods=["GET"])
def admin_get_scoreboard(event_id):
    if not _require_admin_json():
        return jsonify({"status": "error", "message": "Нет доступа"}), 403
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"status": "error", "message": "Игра не найдена"}), 404

    d = event.date
    board = scoreboards.get(event_id, [])
    return jsonify(
        {
            "event_id": event.id,
            "title": event.name,
            "date": f"{d.day} {_MONTHS_RU[d.month]} {d.year}",
            "time": d.strftime("%H:%M"),
            "rounds": SCOREBOARD_ROUNDS,
            "teams": [],
            "scores": board,
        }
    )


@api_bp.route("/admin/games/<int:event_id>/scoreboard", methods=["POST"])
def admin_save_scoreboard(event_id):
    if not _require_admin_json():
        return jsonify({"status": "error", "message": "Нет доступа"}), 403
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"status": "error", "message": "Игра не найдена"}), 404

    payload = request.get_json(silent=True) or {}
    raw_scores = payload.get("scores")
    if not isinstance(raw_scores, list):
        return jsonify({"status": "error", "message": "Неверный формат scores"}), 400

    normalized = []
    for row in raw_scores:
        if not isinstance(row, list):
            return jsonify({"status": "error", "message": "Неверный формат строки"}), 400
        out_row = []
        for cell in row:
            if cell is None or cell == "":
                out_row.append(None)
            else:
                try:
                    v = int(cell)
                except (TypeError, ValueError):
                    return jsonify({"status": "error", "message": "Очки должны быть целыми числами"}), 400
                if v < 0:
                    return jsonify({"status": "error", "message": "Очки не могут быть отрицательными"}), 400
                out_row.append(v)
        normalized.append(out_row)

    trimmed = [(row + [None] * SCOREBOARD_ROUNDS)[:SCOREBOARD_ROUNDS] for row in normalized]
    scoreboards[event_id] = trimmed
    return jsonify({"status": "success", "scores": trimmed})


# Статистика
@api_bp.route("/stats")
def get_stats():
    if not _require_admin_json():
        return jsonify({"status": "error", "message": "Нет доступа"}), 403

    all_events = Event.query.all()
    total_events = len(all_events)
    total_booked = sum(e.booked for e in all_events)
    total_seats = sum(e.seats for e in all_events)
    total_revenue = sum(e.booked * e.price for e in all_events)
    occupancy_rate = round(total_booked / total_seats * 100, 1) if total_seats else 0

    events_list = {}
    for e in all_events:
        photo_url = url_for("pages.serve_media", filename=e.photo) if e.photo else None
        events_list[e.id] = {
            "id": e.id,
            "title": e.name,
            "date": e.date.strftime("%Y-%m-%d"),
            "time": e.date.strftime("%H:%M"),
            "location": e.location,
            "price": e.price,
            "max_seats": e.seats,
            "registered": e.booked,
            "category": e.category,
            "photo": photo_url,
            "photo_path": e.photo,
        }

    top_events = sorted(
        [{"id": e.id, "title": e.name, "registered": e.booked, "max_seats": e.seats} for e in all_events],
        key=lambda x: x["registered"],
        reverse=True,
    )[:3]

    stats = {
        "total_events": total_events,
        "total_revenue": total_revenue,
        "total_attendees": total_booked,
        "occupancy_rate": occupancy_rate,
        "events": events_list,
        "attendance_data": {
            "labels": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
            "values": [120, 150, 180, 200, 220, 250, 180],
        },
        "revenue_data": {
            "labels": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
            "values": [72000, 90000, 108000, 120000, 132000, 150000, 108000],
        },
        "top_events": top_events,
        "event_distribution": {
            "labels": ["Кино", "Музыка", "История", "Другое"],
            "values": [30, 25, 20, 15],
        },
    }
    return jsonify(stats)

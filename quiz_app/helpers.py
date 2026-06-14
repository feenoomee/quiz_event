import os
import uuid

from flask_login import current_user
from flask import current_app, url_for

from datetime import datetime


_MONTHS_RU = [
    "", "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря",
]
_WEEKDAYS_RU = [
    "понедельник", "вторник", "среда", "четверг",
    "пятница", "суббота", "воскресенье",
]

# Для отображение профиля на сайте
def _format_short_name(full_name):
    parts = (full_name or "").split()
    if len(parts) >= 2:
        return f"{parts[-1]} {parts[0][0]}."
    return full_name or "Войти"


def _require_admin_json():
    if not current_user.is_authenticated or current_user.role != "admin":
        return None
    return current_user


def _format_date_ru(dt):
    if not dt:
        return None
    return f"{dt.day} {_MONTHS_RU[dt.month]} {dt.year}"


def _safe_next_url(value):
    if not value or not isinstance(value, str):
        return None
    if not value.startswith("/") or value.startswith("//"):
        return None
    return value


def get_current_user():
    if not current_user.is_authenticated:
        return None
    avatar_url = None
    if current_user.avatar:
        from flask import url_for
        avatar_url = url_for("pages.serve_media", filename=current_user.avatar)
    return {
        "id": current_user.id,
        "name": current_user.name,
        "first_name": current_user.first_name,
        "second_name": current_user.second_name,
        "short_name": _format_short_name(current_user.name),
        "role": current_user.role,
        "email": current_user.email,
        "phone": str(current_user.number_telephone),
        "created_at": _format_date_ru(current_user.created_at),
        "avatar": avatar_url,
    }

def _format_event(event):
    d = event.date or datetime.now()
    photo_url = url_for("pages.serve_media", filename=event.photo) if event.photo else None
    return {
        "id": event.id,
        "title": event.name,
        "description": event.description,
        "category": event.category,
        "date": f"{d.day} {_MONTHS_RU[d.month]} {d.year}, {_WEEKDAYS_RU[d.weekday()]}",
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
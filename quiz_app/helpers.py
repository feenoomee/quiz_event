from flask_login import current_user

_MONTHS_RU = [
    "", "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря",
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
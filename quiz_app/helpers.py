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

# EVENT_TEAMS, SCOREBOARD_ROUNDS, scoreboards - ВРЕМЕННЫЕ ФАЙЛЫ КОТОРЫЕ БЫЛ ДО ЭТОГО, БУДЕТ ЗАМЕНА НА ДАННЫЕ ИЗ БД
def _ensure_scoreboard(event_id):
    teams = EVENT_TEAMS.get(event_id, [])
    if event_id not in scoreboards or len(scoreboards[event_id]) != len(teams):
        scoreboards[event_id] = [_empty_score_row() for _ in teams]
    return scoreboards[event_id]

def _empty_score_row():
    return [None] * SCOREBOARD_ROUNDS

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
    }
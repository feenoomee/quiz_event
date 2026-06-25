from datetime import datetime

import os

from flask import Blueprint, jsonify, request, url_for, current_app
from flask_login import login_required, current_user, login_user
# from werkzeug.utils import secure_filename

from quiz_app import db
from quiz_app.models import User, Event, Team, RegistrationsEvent
from ..helpers import _format_short_name, _require_admin_json, _MONTHS_RU, _format_event, _save_upload #,_allowed_file,  _WEEKDAYS_RU

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/upload/avatar", methods=["POST"])
@login_required
def upload_avatar():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "Файл не передан"}), 400
    file = request.files["file"]
    rel_path = _save_upload(file, "avatars", max_file_size=5*1024*1024, max_size=(300, 300))
    if not rel_path:
        return jsonify({"status": "error", "message": "Недопустимый формат или размер файла (макс. 5 МБ)"}), 400

    if current_user.avatar:
        old_path = os.path.join(current_app.root_path, "media", current_user.avatar)
        if os.path.exists(old_path):
            os.remove(old_path)

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


@api_bp.route("/games/past")
def public_past_games():
    now = datetime.now()
    events = Event.query.filter(Event.scores.isnot(None), Event.scores != '').order_by(Event.date.desc()).limit(20).all()

    result = []
    for event in events:
        regs = RegistrationsEvent.query.filter_by(event_id=event.id).order_by(RegistrationsEvent.id).all()
        teams = [r.team.name for r in regs]

        scores_data = event.get_scores()
        if not scores_data or not teams:
            continue

        team_results = []
        for i, row in enumerate(scores_data):
            if i >= len(teams):
                break
            total = sum(v for v in row if v is not None)
            team_results.append({
                "team_name": teams[i],
                "scores": row,
                "total": total,
            })

        team_results.sort(key=lambda x: x["total"], reverse=True)
        for idx, tr in enumerate(team_results):
            tr["place"] = idx + 1

        d = event.date
        result.append({
            "id": event.id,
            "title": event.name,
            "date": f"{d.day} {_MONTHS_RU[d.month]} {d.year}",
            "time": d.strftime("%H:%M"),
            "location": event.location,
            "photo": url_for("pages.serve_media", filename=event.photo) if event.photo else None,
            "rounds": event.rounds,
            "results": team_results,
        })

    return jsonify({"games": result})


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
    if "rounds" in data:
        try:
            event.rounds = int(data["rounds"])
        except (TypeError, ValueError):
            pass

    date_str = data.get("date")
    time_str = data.get("time")
    if date_str and time_str:
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
            t = datetime.strptime(time_str, "%H:%M").time()
            event.date = datetime.combine(d, t)
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


# Мои команды
@api_bp.route("/my/teams", methods=["GET"])
@login_required
def my_teams():
    teams = current_user.teams
    result = []
    for t in teams:
        result.append({
            "id": t.id,
            "name": t.name,
            "is_captain": t.user_id == current_user.id,
            "members": [{"id": m.id, "name": m.name, "short_name": _format_short_name(m.name)} for m in t.members],
        })
    return jsonify(result)


# Создать команду
@api_bp.route("/teams", methods=["POST"])
@login_required
def create_team():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"status": "error", "message": "Укажите название команды"}), 400

    team = Team(name=name, user_id=current_user.id)
    team.members.append(current_user)
    try:
        db.session.add(team)
        db.session.commit()
        return jsonify({"status": "success", "team": {"id": team.id, "name": team.name}}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Не удалось создать команду"}), 500


# Вступить в команду по id капитана
@api_bp.route("/teams/<int:team_id>/join", methods=["POST"])
@login_required
def join_team(team_id):
    team = Team.query.get(team_id)
    if not team:
        return jsonify({"status": "error", "message": "Команда не найдена"}), 404
    if current_user in team.members:
        return jsonify({"status": "error", "message": "Вы уже в этой команде"}), 409
    team.members.append(current_user)
    try:
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Не удалось присоединиться"}), 500


# Выйти из команды
@api_bp.route("/teams/<int:team_id>/leave", methods=["POST"])
@login_required
def leave_team(team_id):
    team = Team.query.get(team_id)
    if not team:
        return jsonify({"status": "error", "message": "Команда не найдена"}), 404
    if current_user not in team.members:
        return jsonify({"status": "error", "message": "Вы не в этой команде"}), 404
    if team.user_id == current_user.id:
        return jsonify({"status": "error", "message": "Капитан не может выйти из команды. Удалите команду."}), 400
    team.members.remove(current_user)
    try:
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Не удалось выйти"}), 500


# Удалить команду (только капитан)
@api_bp.route("/teams/<int:team_id>", methods=["DELETE"])
@login_required
def delete_team(team_id):
    team = Team.query.get(team_id)
    if not team:
        return jsonify({"status": "error", "message": "Команда не найдена"}), 404
    if team.user_id != current_user.id:
        return jsonify({"status": "error", "message": "Только капитан может удалить команду"}), 403
    try:
        db.session.delete(team)
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Не удалось удалить команду"}), 500


# Мои регистрации
@api_bp.route("/my/registrations", methods=["GET"])
@login_required
def my_registrations():
    from ..helpers import _MONTHS_RU
    auto_cleanup_pending()
    team_ids = [t.id for t in current_user.teams]
    if not team_ids:
        return jsonify([])
    registrations = RegistrationsEvent.query.filter(
        RegistrationsEvent.team_id.in_(team_ids)
    ).order_by(RegistrationsEvent.registered_at.desc()).all()

    result = []
    for reg in registrations:
        ev = reg.event
        team = reg.team
        d = ev.date
        photo_url = url_for("pages.serve_media", filename=ev.photo) if ev.photo else None
        result.append({
            "id": reg.id,
            "event_id": ev.id,
            "event_name": ev.name,
            "event_date": f"{d.day} {_MONTHS_RU[d.month]} {d.year}",
            "event_time": d.strftime("%H:%M"),
            "event_location": ev.location,
            "event_price": ev.price,
            "event_photo": photo_url,
            "team_name": team.name,
            "player_count": reg.player_count,
            "comment": reg.comment,
            "status": reg.status,
            "registered_at": reg.registered_at.isoformat() if reg.registered_at else None,
        })
    return jsonify(result)


# Регистрация команды на ивент
@api_bp.route("/register_team", methods=["POST"])
@login_required
def register_team():
    data = request.get_json(silent=True) or {}
    event_id = data.get("event_id")
    team_id = data.get("team_id")
    player_count = data.get("player_count", 1)
    comment = (data.get("comment") or "").strip()

    if not event_id or not team_id:
        return jsonify({"status": "error", "message": "Укажите мероприятие и команду"}), 400

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"status": "error", "message": "Мероприятие не найдено"}), 404

    team = Team.query.get(team_id)
    if not team:
        return jsonify({"status": "error", "message": "Команда не найдена"}), 404

    if current_user not in team.members:
        return jsonify({"status": "error", "message": "Вы не участник этой команды"}), 403

    existing = RegistrationsEvent.query.filter_by(team_id=team_id, event_id=event_id).first()
    if existing:
        return jsonify({"status": "error", "message": "Команда уже зарегистрирована на это мероприятие"}), 409

    if event.booked >= event.seats:
        return jsonify({"status": "error", "message": "Свободных мест нет"}), 400

    try:
        player_count = int(player_count)
    except (TypeError, ValueError):
        player_count = 1
    if player_count < 1:
        player_count = 1

    reg = RegistrationsEvent(
        team_id=team_id,
        event_id=event_id,
        player_count=player_count,
        comment=comment or None,
        status="pending",
    )
    event.booked += player_count

    try:
        db.session.add(reg)
        db.session.commit()
        return jsonify({"status": "success", "message": "Команда зарегистрирована"}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Не удалось зарегистрироваться"}), 500


# Подтвердить участие
@api_bp.route("/registrations/<int:reg_id>/confirm", methods=["POST"])
@login_required
def confirm_registration(reg_id):
    reg = RegistrationsEvent.query.get(reg_id)
    if not reg:
        return jsonify({"status": "error", "message": "Регистрация не найдена"}), 404
    team = reg.team
    if current_user not in team.members:
        return jsonify({"status": "error", "message": "Нет доступа"}), 403
    if reg.status == "confirmed":
        return jsonify({"status": "success", "message": "Уже подтверждено"})
    reg.status = "confirmed"
    try:
        db.session.commit()
        return jsonify({"status": "success", "message": "Участие подтверждено"})
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Не удалось подтвердить участие"}), 500


def auto_cleanup_pending():
    now = datetime.now()
    from datetime import timedelta
    pending = RegistrationsEvent.query.join(Event).filter(
        RegistrationsEvent.status == "pending",
    ).all()
    pending = [
        reg for reg in pending
        if datetime(reg.event.date.year, reg.event.date.month, reg.event.date.day, 14, 0) <= now
    ]
    removed = 0
    for reg in pending:
        event = reg.event
        if event.booked >= reg.player_count:
            event.booked -= reg.player_count
        else:
            event.booked = 0
        db.session.delete(reg)
        removed += 1
    if removed:
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()


# Отменить регистрацию
@api_bp.route("/registrations/<int:reg_id>", methods=["DELETE"])
@login_required
def cancel_registration(reg_id):
    reg = RegistrationsEvent.query.get(reg_id)
    if not reg:
        return jsonify({"status": "error", "message": "Регистрация не найдена"}), 404
    team = reg.team
    if current_user not in team.members:
        return jsonify({"status": "error", "message": "Нет доступа"}), 403
    event = reg.event
    try:
        db.session.delete(reg)
        if event.booked > 0:
            event.booked -= reg.player_count
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Не удалось отменить регистрацию"}), 500


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


# dmin: недавние игры
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


# Admin: команды, зарегистрированные на мероприятие
@api_bp.route("/admin/events/<int:event_id>/registrations", methods=["GET"])
def admin_event_registrations(event_id):
    if not _require_admin_json():
        return jsonify({"status": "error", "message": "Нет доступа"}), 403
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"status": "error", "message": "Мероприятие не найдено"}), 404

    auto_cleanup_pending()
    regs = RegistrationsEvent.query.filter_by(event_id=event_id).all()
    result = []
    for reg in regs:
        team = reg.team
        members = [{"id": m.id, "name": m.name, "short_name": _format_short_name(m.name)} for m in team.members]
        result.append({
            "id": reg.id,
            "team_id": team.id,
            "team_name": team.name,
            "player_count": reg.player_count,
            "comment": reg.comment,
            "status": reg.status,
            "registered_at": reg.registered_at.isoformat() if reg.registered_at else None,
            "members": members,
        })
    return jsonify({"status": "success", "registrations": result})


# Admin: таблица результатов
@api_bp.route("/admin/games/<int:event_id>/scoreboard", methods=["GET"])
def admin_get_scoreboard(event_id):
    if not _require_admin_json():
        return jsonify({"status": "error", "message": "Нет доступа"}), 403
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"status": "error", "message": "Игра не найдена"}), 404

    d = event.date
    regs = RegistrationsEvent.query.filter_by(event_id=event_id).all()
    teams = [{"name": r.team.name, "index": i} for i, r in enumerate(regs)]
    board = event.get_scores()
    return jsonify(
        {
            "event_id": event.id,
            "title": event.name,
            "date": f"{d.day} {_MONTHS_RU[d.month]} {d.year}",
            "time": d.strftime("%H:%M"),
            "rounds": event.rounds,
            "teams": teams,
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

    trimmed = [(row + [None] * event.rounds)[:event.rounds] for row in normalized]
    event.set_scores(trimmed)
    try:
        db.session.commit()
        return jsonify({"status": "success", "scores": trimmed})
    except Exception:
        db.session.rollback()
        return jsonify({"status": "error", "message": "Не удалось сохранить"}), 500


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
        "top_events": top_events,
    }
    return jsonify(stats)

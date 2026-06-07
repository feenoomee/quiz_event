from flask import Blueprint, jsonify, request, url_for
from flask_login import login_required, current_user, login_user

from quiz_app import db
from quiz_app.models import User, Event

from ..helpers import _format_short_name, _require_admin_json

api_bp = Blueprint( 'api', __name__, url_prefix = '/api' )


# Регистрация нового аккаунта
@api_bp.route( "/register_team", methods = ["POST"] )
def register_team():
    if not current_user.is_authenticated:
        return jsonify( { "status": "error", "message": "Войдите в аккаунт" } ), 401
    return { "status": "success", "message": "Registration received" }


# Вход в аккаунт
@api_bp.route( "/login", methods = ["POST"] )
def login_account():
    payload = request.get_json( silent = True ) or { }
    email = (payload.get( "email" ) or payload.get( "identifier" ) or "").strip().lower()
    password = payload.get( "password" ) or ""
    if not email or not password:
        return jsonify( { "status": "error", "message": "Укажите email и пароль" } ), 400

    user = User.query.filter_by( email = email ).first()
    if not user or not user.check_password( password ):
        return jsonify( { "status": "error", "message": "Неверный email или пароль" } ), 401

    login_user( user )
    return jsonify(
        {
            "status": "success",
            "redirect_to": url_for( "pages.index" ),
            "user": {
                "id": user.id,
                "name": user.name,
                "short_name": _format_short_name( user.name ),
                "role": user.role,
            },
        }
    )


# Регистрация аккаунта
@api_bp.route( "/signup", methods = ["POST"] )
def signup():
    payload = request.get_json( silent = True ) or { }
    first_name = (payload.get( "first_name" ) or "").strip()
    second_name = (payload.get( "second_name" ) or "").strip()
    phone = (payload.get( "phone" ) or "").strip()
    email = (payload.get( "email" ) or "").strip().lower()
    password = payload.get( "password" ) or ""

    if not all( [first_name, second_name, phone, email, password] ):
        return jsonify( { "status": "error", "message": "Заполните все поля регистрации" } ), 400

    if User.query.filter_by( email = email ).first():
        return jsonify( { "status": "error", "message": "Пользователь с таким email уже существует" } ), 409

    user = User(
        first_name = first_name,
        second_name = second_name,
        email = email,
        role = "user",
        number_telephone = phone,
    )
    user.set_password(  password )

    try:
        db.session.add( user )
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify( { "status": "error", "message": "Не удалось создать аккаунт" } ), 500

    login_user( user )
    return jsonify(
        {
            "status": "success",
            "redirect_to": url_for( "index" ),
            "user": {
                "id": user.id,
                "name": user.name,
                "short_name": _format_short_name( user.name ),
                "role": user.role,
            },
        }
    ), 201


@api_bp.route( "/profile", methods = ["PUT"] )
@login_required
def update_profile():
    payload = request.get_json( silent = True ) or { }
    first_name = (payload.get( "first_name" ) or "").strip()
    second_name = (payload.get( "second_name" ) or "").strip()
    email = (payload.get( "email" ) or "").strip().lower()
    phone = (payload.get( "phone" ) or "").strip()

    if not all( [first_name, second_name, email] ):
        return jsonify( { "status": "error", "message": "Имя, фамилия и email обязательны" } ), 400

    if email != current_user.email:
        existing = User.query.filter_by( email = email ).first()
        if existing:
            return jsonify( { "status": "error", "message": "Этот email уже занят" } ), 409

    current_user.first_name = first_name
    current_user.second_name = second_name
    current_user.email = email
    if phone:
        current_user.number_telephone = phone

    try:
        db.session.commit()
        return jsonify( { "status": "success", "message": "Профиль обновлён" } )
    except Exception:
        db.session.rollback()
        return jsonify( { "status": "error", "message": "Не удалось сохранить" } ), 500


@api_bp.route( "/admin/recent-games" )
def admin_recent_games():
    if not _require_admin_json():
        return jsonify( { "status": "error", "message": "Нет доступа" } ), 403
    limit = request.args.get( "limit", default = 15, type = int ) or 15
    limit = max( 1, min( limit, 50 ) )
    rows = []
    for eid, ev in events.items():
        rows.append(
            {
                "id": eid,
                "title": ev["title"],
                "date": ev["date"],
                "time": ev["time"],
                "location": ev.get( "location", "" ),
            }
        )
    rows.sort( key = lambda r: (r["date"], r["time"]), reverse = True )
    return jsonify( { "games": rows[:limit] } )

# Подтягивай данные из бд
# API для заполнение таблицы в профиле админа - дальше планируется отображать её на главной странице
@api_bp.route( "/admin/games/<int:event_id>/scoreboard", methods = ["GET"] )
def admin_get_scoreboard( event_id ):
    if not _require_admin_json():
        return jsonify( { "status": "error", "message": "Нет доступа" } ), 403
    if event_id not in events:
        return jsonify( { "status": "error", "message": "Игра не найдена" } ), 404
    ev = events[event_id]
    teams = EVENT_TEAMS.get( event_id, [] )
    board = _ensure_scoreboard( event_id )
    return jsonify(
        {
            "event_id": event_id,
            "title": ev["title"],
            "date": ev["date"],
            "time": ev["time"],
            "rounds": SCOREBOARD_ROUNDS,
            "teams": [{ "index": i, "name": name } for i, name in enumerate( teams )],
            "scores": board,
        }
    )


@api_bp.route( "/admin/games/<int:event_id>/scoreboard", methods = ["POST"] )
def admin_save_scoreboard( event_id ):
    if not _require_admin_json():
        return jsonify( { "status": "error", "message": "Нет доступа" } ), 403
    if event_id not in events:
        return jsonify( { "status": "error", "message": "Игра не найдена" } ), 404
    teams = EVENT_TEAMS.get( event_id, [] )
    payload = request.get_json( silent = True ) or { }
    raw_scores = payload.get( "scores" )
    if not isinstance( raw_scores, list ) or len( raw_scores ) != len( teams ):
        return jsonify( { "status": "error", "message": "Неверный формат scores" } ), 400
    normalized = []
    for row in raw_scores:
        if not isinstance( row, list ) or len( row ) != SCOREBOARD_ROUNDS:
            return jsonify( { "status": "error", "message": "Нужно по 7 значений на команду" } ), 400
        out_row = []
        for cell in row:
            if cell is None or cell == "":
                out_row.append( None )
            else:
                try:
                    v = int( cell )
                except (TypeError, ValueError):
                    return jsonify( { "status": "error", "message": "Очки должны быть целыми числами" } ), 400
                if v < 0:
                    return jsonify( { "status": "error", "message": "Очки не могут быть отрицательными" } ), 400
                out_row.append( v )
        normalized.append( out_row )
    scoreboards[event_id] = normalized
    return jsonify( { "status": "success", "scores": normalized } )


@api_bp.route( "/stats" )
def get_stats():
    stats = {
        "total_events": len( events ),
        "total_revenue": sum( e["registered"] * e["price"] for e in events.values() ),
        "total_attendees": sum( e["registered"] for e in events.values() ),
        "occupancy_rate": round(
            sum( e["registered"] for e in events.values() )
            / sum( e["max_seats"] for e in events.values() )
            * 100,
            1,
        ),
        "events": events,
        "attendance_data": {
            "labels": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
            "values": [120, 150, 180, 200, 220, 250, 180],
        },
        "revenue_data": {
            "labels": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
            "values": [72000, 90000, 108000, 120000, 132000, 150000, 108000],
        },
        "top_events": sorted( events.values(), key = lambda x: x["registered"], reverse = True )[:3],
        "event_distribution": {
            "labels": ["Кино", "Музыка", "История", "Другое"],
            "values": [30, 25, 20, 15],
        },
    }
    return jsonify( stats )

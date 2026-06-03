import os

from flask import jsonify, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required, login_user, logout_user

from . import db
from .models import User


events = {
    1: {
        "title": "Кино и сериалы 2025",
        "date": "2026-06-13",
        "time": "19:00",
        "location": "ТЦ Ёлки",
        "max_seats": 30,
        "registered": 24,
        "price": 600,
    },
    2: {
        "title": "Угадай мелодию",
        "date": "2026-06-20",
        "time": "20:00",
        "location": "ТЦ Ёлки",
        "max_seats": 25,
        "registered": 18,
        "price": 550,
    },
    3: {
        "title": "История и культура",
        "date": "2026-06-27",
        "time": "19:00",
        "location": "Клуб 360",
        "max_seats": 35,
        "registered": 32,
        "price": 650,
    },
    4: {
        "title": "Наука и технологии",
        "date": "2026-07-04",
        "time": "18:00",
        "location": "Коворкинг Старт",
        "max_seats": 20,
        "registered": 15,
        "price": 500,
    },
    5: {
        "title": "География мира",
        "date": "2026-07-11",
        "time": "20:00",
        "location": "Бар Квиз",
        "max_seats": 40,
        "registered": 38,
        "price": 700,
    },
}

# Демо: команды по событиям (замена на регистрации из БД)
EVENT_TEAMS = {
    1: ["ПО КОЛЕНО!", "Квиз-пати", "Мозголомы", "Три кота", "Ночные совы"],
    2: ["Мелодисты", "Дикие ноты", "Оркестр"],
    3: ["Историки", "Культура превыше всего", "Память века", "Хроники"],
    4: ["Квантовый разум", "Техно-гики", "Инноваторы"],
    5: ["Планета Земля", "Путешественники", "Картографы", "Миротворцы", "Атлас"],
}

# Число туров в таблице (как на макете)
SCOREBOARD_ROUNDS = 7

# Сохранённые очки: event_id -> [[t1r1..t1r7], [t2r1..], ...] (None = пусто)
scoreboards = {
    1: [
        [19, 15, 26, None, None, None, None],
        [18, 14, 22, None, None, None, None],
        [17, 16, 20, None, None, None, None],
        [16, 12, 18, None, None, None, None],
        [15, 13, 19, None, None, None, None],
    ],
    2: [
        [20, 18, 24, None, None, None, None],
        [19, 16, 22, None, None, None, None],
        [18, 17, 20, None, None, None, None],
    ],
    3: [
        [22, 19, 28, None, None, None, None],
        [21, 18, 26, None, None, None, None],
        [20, 17, 24, None, None, None, None],
        [19, 16, 22, None, None, None, None],
    ],
    4: [
        [17, 14, 20, None, None, None, None],
        [16, 15, 18, None, None, None, None],
        [15, 13, 17, None, None, None, None],
    ],
    5: [
        [25, 22, 30, None, None, None, None],
        [24, 21, 28, None, None, None, None],
        [23, 20, 26, None, None, None, None],
        [22, 19, 24, None, None, None, None],
        [21, 18, 22, None, None, None, None],
    ],
}


def _require_admin_json():
    if not current_user.is_authenticated or current_user.role != "admin":
        return None
    return current_user


def _empty_score_row():
    return [None] * SCOREBOARD_ROUNDS


def _ensure_scoreboard(event_id):
    teams = EVENT_TEAMS.get(event_id, [])
    if event_id not in scoreboards or len(scoreboards[event_id]) != len(teams):
        scoreboards[event_id] = [_empty_score_row() for _ in teams]
    return scoreboards[event_id]


def _format_short_name(full_name):
    parts = (full_name or "").split()
    if len(parts) >= 2:
        return f"{parts[-1]} {parts[0][0]}."
    return full_name or "Кабинет"


_MONTHS_RU = [
    "", "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря",
]


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


def register_routes(app):
    @app.context_processor
    def inject_current_user():
        return {"current_user": get_current_user()}

    @app.route("/")
    def index():
        return render_template("pages/index.html")

    @app.route("/media/<filename>")
    def serve_media(filename):
        """Файлы из папки media/ рядом с приложением (как раньше в app.py)."""
        return send_from_directory(os.path.join(app.root_path, "media"), filename)

    @app.route("/api/register", methods=["POST"])
    def register_team():
        if not current_user.is_authenticated:
            return jsonify({"status": "error", "message": "Войдите в аккаунт"}), 401
        return {"status": "success", "message": "Registration received"}

    @app.route("/profile")
    @login_required
    def profile():
        current_user = get_current_user()
        if not current_user:
            return redirect(url_for("index"))
        return render_template("pages/profile.html", current_user=current_user)

    @app.route("/admin")
    @login_required
    def admin():
        current_user = get_current_user()
        if not current_user:
            return redirect(url_for("index"))
        if current_user["role"] != "admin":
            return redirect(url_for("profile"))
        return render_template("pages/admin.html", current_user=current_user)

    @app.route("/dashboard")
    @login_required
    def dashboard():
        current_user = get_current_user()
        if not current_user:
            return redirect(url_for("index"))
        if current_user["role"] == "admin":
            return redirect(url_for("admin"))
        return redirect(url_for("profile"))

    @app.route("/api/login", methods=["POST"])
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
                "redirect_to": url_for("index"),
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "short_name": _format_short_name(user.name),
                    "role": user.role,
                },
            }
        )

    @app.route("/api/signup", methods=["POST"])
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
        user.sd(password)

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
                "redirect_to": url_for("index"),
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "short_name": _format_short_name(user.name),
                    "role": user.role,
                },
            }
        ), 201

    @app.route("/api/profile", methods=["PUT"])
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

    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for("index"))

    @app.route("/api/admin/recent-games")
    def admin_recent_games():
        if not _require_admin_json():
            return jsonify({"status": "error", "message": "Нет доступа"}), 403
        limit = request.args.get("limit", default=15, type=int) or 15
        limit = max(1, min(limit, 50))
        rows = []
        for eid, ev in events.items():
            rows.append(
                {
                    "id": eid,
                    "title": ev["title"],
                    "date": ev["date"],
                    "time": ev["time"],
                    "location": ev.get("location", ""),
                }
            )
        rows.sort(key=lambda r: (r["date"], r["time"]), reverse=True)
        return jsonify({"games": rows[:limit]})

    @app.route("/api/admin/games/<int:event_id>/scoreboard", methods=["GET"])
    def admin_get_scoreboard(event_id):
        if not _require_admin_json():
            return jsonify({"status": "error", "message": "Нет доступа"}), 403
        if event_id not in events:
            return jsonify({"status": "error", "message": "Игра не найдена"}), 404
        ev = events[event_id]
        teams = EVENT_TEAMS.get(event_id, [])
        board = _ensure_scoreboard(event_id)
        return jsonify(
            {
                "event_id": event_id,
                "title": ev["title"],
                "date": ev["date"],
                "time": ev["time"],
                "rounds": SCOREBOARD_ROUNDS,
                "teams": [{"index": i, "name": name} for i, name in enumerate(teams)],
                "scores": board,
            }
        )

    @app.route("/api/admin/games/<int:event_id>/scoreboard", methods=["POST"])
    def admin_save_scoreboard(event_id):
        if not _require_admin_json():
            return jsonify({"status": "error", "message": "Нет доступа"}), 403
        if event_id not in events:
            return jsonify({"status": "error", "message": "Игра не найдена"}), 404
        teams = EVENT_TEAMS.get(event_id, [])
        payload = request.get_json(silent=True) or {}
        raw_scores = payload.get("scores")
        if not isinstance(raw_scores, list) or len(raw_scores) != len(teams):
            return jsonify({"status": "error", "message": "Неверный формат scores"}), 400
        normalized = []
        for row in raw_scores:
            if not isinstance(row, list) or len(row) != SCOREBOARD_ROUNDS:
                return jsonify({"status": "error", "message": "Нужно по 7 значений на команду"}), 400
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
        scoreboards[event_id] = normalized
        return jsonify({"status": "success", "scores": normalized})

    @app.route("/api/stats")
    def get_stats():
        stats = {
            "total_events": len(events),
            "total_revenue": sum(e["registered"] * e["price"] for e in events.values()),
            "total_attendees": sum(e["registered"] for e in events.values()),
            "occupancy_rate": round(
                sum(e["registered"] for e in events.values())
                / sum(e["max_seats"] for e in events.values())
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
            "top_events": sorted(events.values(), key=lambda x: x["registered"], reverse=True)[:3],
            "event_distribution": {
                "labels": ["Кино", "Музыка", "История", "Другое"],
                "values": [30, 25, 20, 15],
            },
        }
        return jsonify(stats)

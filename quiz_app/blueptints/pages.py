import os

from flask import Blueprint, url_for, send_from_directory, current_app, redirect, render_template
from flask_login import login_required, current_user, logout_user

from ..helpers import get_current_user, _MONTHS_RU

pages_bp = Blueprint( "pages", __name__)


_WEEKDAYS_RU = [
    "понедельник", "вторник", "среда", "четверг",
    "пятница", "суббота", "воскресенье",
]


@pages_bp.context_processor
def inject_current_user():
    return { "current_user": get_current_user() }


@pages_bp.route( "/" )
def index():
    from datetime import datetime
    from quiz_app.models import Event
    now = datetime.now()
    nearest = Event.query.filter(Event.date >= now).order_by(Event.date).first()
    nearest_event = None
    if nearest:
        d = nearest.date
        date_ru = f"{d.day} {_MONTHS_RU[d.month]}, {_WEEKDAYS_RU[d.weekday()]}"
        seats_left = nearest.seats - nearest.booked
        nearest_event = {
            "id": nearest.id,
            "name": nearest.name,
            "date": date_ru,
            "time": d.strftime("%H:%M"),
            "location": nearest.location,
            "price": nearest.price,
            "seats": nearest.seats,
            "booked": nearest.booked,
            "seats_left": seats_left,
        }
    return render_template( "pages/index.html", nearest_event=nearest_event )


@pages_bp.route( "/media/<filename>" )
def serve_media( filename ):
    """Файлы из папки media/ рядом с приложением (как раньше в app.py)."""
    return send_from_directory( os.path.join( current_app.root_path, "media" ), filename )


@pages_bp.route( "/profile" )
@login_required
def profile():
    current_user = get_current_user()
    if not current_user:
        return redirect( url_for( "pages.index" ) )
    return render_template( "pages/profile.html", current_user = current_user )


@pages_bp.route( "/admin" )
@login_required
def admin():
    current_user = get_current_user()
    if not current_user:
        return redirect( url_for( "pages.index" ) )
    if current_user["role"] != "admin":
        return redirect( url_for( "pages.profile" ) )
    return render_template( "pages/admin.html", current_user = current_user )


@pages_bp.route( "/dashboard" )
@login_required
def dashboard():
    current_user = get_current_user()
    if not current_user:
        return redirect( url_for( "pages.index" ) )
    if current_user["role"] == "admin":
        return redirect( url_for( "pages.admin" ) )
    return redirect( url_for( "pages.profile" ) )


@pages_bp.route( "/logout" )
def logout():
    logout_user()
    return redirect( url_for( "pages.index" ) )

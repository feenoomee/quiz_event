import os

from flask import Blueprint, url_for, send_from_directory, current_app, redirect, render_template
from flask_login import login_required, current_user, logout_user

from ..helpers import get_current_user

pages_bp = Blueprint( "pages", __name__)


@pages_bp.context_processor
def inject_current_user():
    return { "current_user": get_current_user() }


@pages_bp.route( "/" )
def index():
    return render_template( "pages/index.html" )


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

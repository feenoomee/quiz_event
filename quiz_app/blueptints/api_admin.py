#импорт библиотек и нужных модулей
import os

from flask import Blueprint, jsonify, request, url_for, current_app
from flask_login import login_required, current_user, login_user

from quiz_app import db
from quiz_app.models import User, Event, Team, RegistrationsEvent, SitePoster

from ..helpers import _format_short_name, _require_admin_json, _MONTHS_RU, _format_event, _save_upload, _format_date_ru, _save_image_upload




api_admin_bp = Blueprint("api_admin", __name__, url_prefix="/api")

@api_admin_bp.route("/upload/event-photo", methods=["POST"])
@login_required
def upload_event_photo():
    
    if not _require_admin_json():
        return jsonify({"status": "error", "message": "Нет доступа"}), 403
    
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "Файл не передан"}), 400
    
    file = request.files["file"]
    rel_path = _save_upload(file, "events", max_size=(2000, 2000))
    
    if not rel_path:
        return jsonify({"status": "error", "message": "Недопустимый формат файла"}), 400
    photo_url = url_for("pages.serve_media", filename=rel_path)
    
    return jsonify({"status": "success", "url": photo_url, "path": rel_path})


@api_admin_bp.route("/upload/result-photo", methods=["POST"])
@login_required
def upload_result_photo():
    if not _require_admin_json():
        return jsonify({"status": "error", "message": "No access"}), 403
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "File is required"}), 400
    file = request.files["file"]
    rel_path = _save_image_upload(
        file,
        "results",
        max_file_size=16 * 1024 * 1024,
    )
    if not rel_path:
        return jsonify({"status": "error", "message": "Недопустимый формат файла или файл больше 16 МБ"}), 400
    photo_url = url_for("pages.serve_media", filename=rel_path)
    return jsonify({"status": "success", "url": photo_url, "path": rel_path})
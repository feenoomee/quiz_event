"""
Пакет Flask-приложения TLTQUIZ (макет + демо-логика).

Дальше: сюда же blueprints, инициализация БД, регистрация CLI-команд.
"""
import os

from flask import Flask

from .config import Config

# Каталог проекта (родитель пакета quiz_app/) — здесь лежат templates/ и static/
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def create_app(config_class=Config):
    app = Flask(
        __name__,
        root_path=_PROJECT_ROOT,
        template_folder=os.path.join(_PROJECT_ROOT, "templates"),
        static_folder=os.path.join(_PROJECT_ROOT, "static"),
    )
    app.config.from_object(config_class)

    from . import routes

    routes.register_routes(app)
    return app

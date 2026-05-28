import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


from .config import Config


_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(
        __name__,
        root_path=_PROJECT_ROOT,
        template_folder=os.path.join(_PROJECT_ROOT, "templates"),
        static_folder=os.path.join(_PROJECT_ROOT, "static"),
    )
    app.config.from_object(config_class)

    db.init_app(app)
    migrate = Migrate( app, db )

    from . import models, routes

    routes.register_routes(app)
    return app

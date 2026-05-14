# Конфигурация приложения. Позже: SECRET_KEY из окружения, URI БД, почта и т.д.
import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-here")

    # Пример для SQLAlchemy (раскомментируй при подключении БД):
    # SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///instance/quiz.db")
    # SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True

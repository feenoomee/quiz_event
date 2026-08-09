"""Точка входа для Passenger на шаред-хостинге Рег.ру (ispmanager).

Путь к venv определяется через ~ (домашний каталог пользователя хостинга),
поэтому менять логин не требуется. Venv должен называться ``flaskenv``.
"""
import sys
import os

INTERP = os.path.expanduser("/var/www/u3594619/data/flaskenv/bin/python")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())

from app import app as application

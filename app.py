"""
Точка входа для запуска и для ``from app import app`` (run.py, Flask CLI).

Логика приложения находится в пакете ``quiz_app`` (фабрика ``create_app``).
"""
import os

from quiz_app import create_app

app = create_app()

if not os.environ.get("WERKZEUG_RUN_MAIN"):
    from quiz_app.scheduler import init_scheduler
    init_scheduler(app)

if __name__ == "__main__":
    app.run(debug=True, host = '0.0.0.0')

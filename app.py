"""
Точка входа для запуска и для ``from app import app`` (run.py, Flask CLI).

Логика приложения находится в пакете ``quiz_app`` (фабрика ``create_app``).
"""
from quiz_app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

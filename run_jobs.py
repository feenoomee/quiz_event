"""Разовый запуск фоновых задач для cron на хостинге Рег.ру (ispmanager).

В панели ispmanager (раздел «Запланированные задания»/Cron) добавьте задание,
например один раз в час:

    ~/flaskenv/bin/python ~/www/run_jobs.py

или через прямой путь (подставьте свой логин uXXXXXXX):

    /var/www/uXXXXXXX/data/flaskenv/bin/python /var/www/uXXXXXXX/data/www/run_jobs.py

Джоба выполняет: ежедневные напоминания о подтверждении участия
(одно на команду — повторно не отправляются), автоотмену неподтверждённых
регистраций после 13:00 и очистку событий старше 6 месяцев.
Частый запуск (раз в час) безопасен: напоминания и автоотмена
срабатывают не более одного раза.
"""
from quiz_app import create_app
from quiz_app.scheduler import run_jobs_once


if __name__ == "__main__":
    app = create_app()
    run_jobs_once(app)

from datetime import datetime, timedelta
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from quiz_app import create_app, db as _db
from quiz_app.models import Event

app = create_app()

with app.app_context():
    now = datetime.now()

    events_data = [
        ("Кинохиты 2020", "cinema", now - timedelta(days=179), "Бар Кино", 20, 600),
        ("Музыка 90-х", "music", now - timedelta(days=120), "Рок-бар", 15, 500),
        ("Классика жанра", "classic", now - timedelta(days=60), "Паб 42", 25, 550),
        ("Шоу талантов", "show", now - timedelta(days=30), "Концерт-холл", 30, 700),
        ("Угадай мелодию", "music", now - timedelta(days=7), "Бар Аккорд", 20, 500),
        ("Киноквиз: боевики", "cinema", now + timedelta(days=7), "Кинотеатр", 25, 650),
        ("Рок-легенды", "music", now + timedelta(days=14), "Рок-бар", 20, 550),
        ("Интеллект-батл", "classic", now + timedelta(days=30), "Антикафе", 15, 400),
        ("Шоу импровизация", "show", now + timedelta(days=45), "Театр", 35, 800),
        ("Новогодний квиз", "cinema", now + timedelta(days=60), "Ресторан", 40, 1000),
    ]

    for name, category, date, location, seats, price in events_data:
        ev = Event(
            name=name,
            description=f"Тестовое мероприятие: {name}",
            category=category,
            date=date,
            location=location,
            seats=seats,
            price=price,
            booked=0,
        )
        _db.session.add(ev)

    _db.session.commit()
    print(f"Создано {len(events_data)} мероприятий:")
    for name, _, date, *_ in events_data:
        prefix = "[FUTURE]" if date > datetime.now() else "[PAST]"
        print(f"  {prefix} {name} - {date.strftime('%d.%m.%Y')}")

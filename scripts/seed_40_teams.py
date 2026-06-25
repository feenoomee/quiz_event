import random
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from quiz_app import create_app
from quiz_app.models import Event, Team, RegistrationsEvent, User, db

EVENT_ID = 1
TEAM_COUNT = 40
ROUNDS = 7

TEAM_NAMES = [
    "Квизмастера", "Ушастые интеллектуалы", "Звёздные мозги",
    "Профессора диванных наук", "Нейронные сети", "Биги Мозги",
    "Турбо-Мозг", "Эрудит", "Логика", "Вундеркинды",
    "Гении чила", "Дикие квизёры", "Атомные мозги", "IQшки",
    "Почти умные", "Ботаники", "Шпроты", "Мегамозг",
    "Пенсионеры", "Рандом", "Умники и умницы", "Дети подземелья",
    "ЧВК Эрудит", "Пельмени", "Головоломка", "Ребус",
    "Кукуруза", "Панда", "Фламинго", "Суслики",
    "Квиззи", "Индиго", "Сириус", "Альфа",
    "Бетта", "Гамма", "Дельта", "Эпсилон",
    "Зета", "Эта"
]

app = create_app()
with app.app_context():
    event = Event.query.get(EVENT_ID)
    if not event:
        print(f"Ошибка: событие с ID {EVENT_ID} не найдено")
        sys.exit(1)

    print(f"Событие: {event.name}, раундов: {event.rounds}")

    user_ids = [u.id for u in User.query.all()]
    if not user_ids:
        print("Ошибка: нет пользователей в БД")
        sys.exit(1)
    print(f"Пользователей для привязки: {len(user_ids)}")

    RegistrationsEvent.query.filter_by(event_id=EVENT_ID).delete()
    db.session.flush()

    Team.query.delete()
    db.session.flush()

    teams = []
    for i in range(TEAM_COUNT):
        name = TEAM_NAMES[i] if i < len(TEAM_NAMES) else f"Команда {i + 1}"
        team = Team(name=name, user_id=random.choice(user_ids))
        db.session.add(team)
        db.session.flush()
        teams.append(team)

    regs = []
    total_players = 0
    for t in teams:
        is_confirmed = random.random() < 0.7
        player_count = random.randint(4, 8)
        reg = RegistrationsEvent(
            team_id=t.id,
            event_id=EVENT_ID,
            player_count=player_count,
            comment=random.choice(["", "Будем", "Готовы", "Опаздываем на 5 мин", None]),
            status="confirmed" if is_confirmed else "pending",
        )
        db.session.add(reg)
        db.session.flush()
        regs.append(reg)
        total_players += player_count

    event.booked = total_players
    db.session.commit()
    print(f"Создано {len(teams)} команд, зарегистрировано {len(regs)}")

    scores = []
    for _ in regs:
        row = [random.randint(0, 12) for _ in range(ROUNDS)]
        scores.append(row)

    event.set_scores(scores)
    db.session.commit()
    print(f"Результаты сохранены для {len(scores)} команд")

    team_results = []
    for i, reg in enumerate(regs):
        total = sum(scores[i])
        team_results.append({"name": reg.team.name, "total": total})

    team_results.sort(key=lambda x: x["total"], reverse=True)

    print(f"\n=== ИТОГОВАЯ ТАБЛИЦА ({len(team_results)} команд) ===")
    for i, tr in enumerate(team_results):
        print(f"  {i + 1}. {tr['name']} — {tr['total']} баллов")

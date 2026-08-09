import datetime as _dt
import os
import sys

import pytest
from werkzeug.security import generate_password_hash

os.environ.setdefault("SECRET_KEY", "test-secret-key")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from quiz_app import create_app, db as _db
from quiz_app.models import User, Event, Team, RegistrationsEvent


@pytest.fixture(scope="session")
def app():
    from quiz_app.config import TestingConfig

    _app = create_app(TestingConfig)
    yield _app


@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app, db):
    return app.test_client()


@pytest.fixture
def user(client):
    """Register a user via /api/signup, return client."""
    client.post(
        "/api/signup",
        json={
            "first_name": "Test",
            "second_name": "User",
            "phone": "+79001234567",
            "email": "test@example.com",
            "password": "pass123",
        },
    )
    return client


@pytest.fixture
def admin_client(app, db):
    """Create admin user in DB, login, return a fresh client."""
    admin = User(
        first_name="Admin",
        second_name="Adminov",
        email="admin@test.com",
        number_telephone="+79000000000",
        password_hash=generate_password_hash("admin123"),
        role="admin",
    )
    db.session.add(admin)
    db.session.commit()

    c = app.test_client()
    c.post(
        "/api/login",
        json={"email": "admin@test.com", "password": "admin123"},
    )
    return c


def _create_user(email, first_name="U", second_name="S", phone="+79000000000"):
    """Create a user directly in DB (no API, no session side-effects)."""
    user = User(
        first_name=first_name,
        second_name=second_name,
        email=email,
        number_telephone=phone,
        password_hash=generate_password_hash("pass123"),
        role="user",
    )
    _db.session.add(user)
    _db.session.flush()
    return user


@pytest.fixture
def make_event(app, db):
    """Factory fixture: creates an Event with the given params."""
    def _make(
        event_date=None,
        booked=0,
        seats=10,
        price=500,
        name="Тестовое событие",
    ):
        if event_date is None:
            event_date = _dt.datetime.now() + _dt.timedelta(days=1)
        elif isinstance(event_date, _dt.date) and not isinstance(event_date, _dt.datetime):
            event_date = _dt.datetime.combine(event_date, _dt.time(18, 0))
        ev = Event(
            name=name,
            description="Тест",
            category="5x5",
            date=event_date,
            location="Тестовый клуб",
            seats=seats,
            price=price,
            booked=booked,
        )
        db.session.add(ev)
        db.session.commit()
        return ev

    return _make


@pytest.fixture
def make_team(app, db):
    """Create a team. If the captain doesn't exist, create it in DB."""

    def _make(captain_email="test@example.com", name="Test Team"):
        captain = User.query.filter_by(email=captain_email).first()
        if captain is None:
            captain = _create_user(captain_email)
        team = Team(name=name, user_id=captain.id)
        team.members.append(captain)
        db.session.add(team)
        db.session.commit()
        return team

    return _make


@pytest.fixture
def make_waitlist_team(app, db, make_event, make_team):
    """Factory fixture: creates a confirmed waitlisted registration."""

    def _make(captain_email="test@example.com"):
        ev = make_event(booked=10, seats=10)
        team = make_team(captain_email=captain_email, name="WL Team")
        reg = RegistrationsEvent(
            team_id=team.id,
            event_id=ev.id,
            player_count=5,
            status="pending",
            waitlist=True,
        )
        db.session.add(reg)
        db.session.commit()
        return ev, team, reg

    return _make

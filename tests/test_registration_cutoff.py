"""Tests for 13:00 cutoff — no registrations after 13:00 on event day."""
import datetime as _dt
from unittest.mock import patch


class FakeDatetime:
    """Replaces datetime module-level import for time-sensitive tests.

    Supports:
      - FakeDatetime(y, m, d, H, M)  → returns a fixed datetime
      - FakeDatetime.now()            → returns the same fixed datetime
    """

    def __init__(self, fixed):
        self._fixed = fixed

    def __call__(self, *args, **kwargs):
        if args:
            return _dt.datetime(*args, **kwargs)
        return self._fixed

    def now(self, tz=None):
        return self._fixed

    def __ge__(self, other):
        return self._fixed >= other

    def __le__(self, other):
        return self._fixed <= other

    def __gt__(self, other):
        return self._fixed > other

    def __lt__(self, other):
        return self._fixed < other

    def strptime(self, *args, **kwargs):
        return _dt.datetime.strptime(*args, **kwargs)


class TestRegistrationCutoff:
    """POST /api/register_team must block after 13:00 on event day."""

    def test_register_after_13h_blocked(self, user, make_event, make_team):
        today = _dt.date.today()
        ev = make_event(event_date=_dt.datetime.combine(today, _dt.time(18, 0)))
        team = make_team(name="Late Team")
        fixed = _dt.datetime.combine(today, _dt.time(13, 1))

        with patch("quiz_app.blueptints.api.datetime", FakeDatetime(fixed)):
            resp = user.post(
                "/api/register_team",
                json={"event_id": ev.id, "team_id": team.id, "player_count": 5},
            )
        assert resp.status_code == 400
        assert "13:00" in resp.get_json()["message"]

    def test_register_before_13h_allowed(self, user, make_event, make_team):
        today = _dt.date.today()
        ev = make_event(event_date=_dt.datetime.combine(today, _dt.time(18, 0)))
        team = make_team(name="On Time Team")
        fixed = _dt.datetime.combine(today, _dt.time(12, 59))

        with patch("quiz_app.blueptints.api.datetime", FakeDatetime(fixed)):
            resp = user.post(
                "/api/register_team",
                json={"event_id": ev.id, "team_id": team.id, "player_count": 5},
            )
        assert resp.status_code == 201

    def test_register_after_13h_future_event_allowed(self, user, make_event, make_team):
        today = _dt.date.today()
        tomorrow = today + _dt.timedelta(days=1)
        ev = make_event(event_date=_dt.datetime.combine(tomorrow, _dt.time(18, 0)))
        team = make_team(name="Future Team")
        fixed = _dt.datetime.combine(today, _dt.time(14, 0))

        with patch("quiz_app.blueptints.api.datetime", FakeDatetime(fixed)):
            resp = user.post(
                "/api/register_team",
                json={"event_id": ev.id, "team_id": team.id, "player_count": 5},
            )
        assert resp.status_code == 201


class TestAutoCleanupPendingAfterDeadline:
    """auto_cleanup_pending removes non-waitlist pending after deadline."""

    def test_cleanup_removes_non_waitlist_pending_after_deadline(
        self, app, db, user, make_event, make_team
    ):
        from quiz_app.models import RegistrationsEvent
        with app.app_context():
            from quiz_app import db as _db
            from quiz_app.blueptints.api import auto_cleanup_pending

            ev = make_event(event_date=_dt.datetime.now() - _dt.timedelta(days=1))
            team = make_team(name="Cleanup Team")
            reg = RegistrationsEvent(
                team_id=team.id, event_id=ev.id,
                status="pending", waitlist=False,
            )
            _db.session.add(reg)
            _db.session.commit()
            auto_cleanup_pending()
            assert RegistrationsEvent.query.get(reg.id) is None

    def test_cleanup_preserves_waitlist_pending_after_deadline(
        self, app, db, user, make_event, make_team
    ):
        from quiz_app.models import RegistrationsEvent
        with app.app_context():
            from quiz_app import db as _db
            from quiz_app.blueptints.api import auto_cleanup_pending

            ev = make_event(booked=10, seats=10,
                            event_date=_dt.datetime.now() - _dt.timedelta(hours=1))
            team = make_team(name="WL Cleanup Team")
            reg = RegistrationsEvent(
                team_id=team.id, event_id=ev.id,
                status="pending", waitlist=True,
            )
            _db.session.add(reg)
            _db.session.commit()
            auto_cleanup_pending()
            assert RegistrationsEvent.query.get(reg.id) is not None

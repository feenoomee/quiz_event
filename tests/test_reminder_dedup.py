"""Tests that scheduler reminders are sent exactly once per registration."""
import datetime as _dt
from unittest.mock import patch


class TestReminderDedup:
    def test_reminder_sent_only_once(self, app, db, make_event, make_team):
        from quiz_app import db as _db
        from quiz_app.models import RegistrationsEvent
        from quiz_app import scheduler

        with app.app_context():
            today = _dt.datetime.now().date()
            ev = make_event(event_date=_dt.datetime.combine(today, _dt.time(18, 0)))
            team = make_team(name="Once Team")
            reg = RegistrationsEvent(
                team_id=team.id,
                event_id=ev.id,
                status="pending",
                waitlist=False,
            )
            _db.session.add(reg)
            _db.session.commit()

            scheduler._app_instance = app

            with patch("quiz_app.scheduler.send_reminder_email") as mock_send:
                scheduler.send_reminders()
                scheduler.send_reminders()
                scheduler.send_reminders()

            assert mock_send.call_count == 1
            assert RegistrationsEvent.query.get(reg.id).reminder_sent_at is not None

    def test_confirmed_registration_gets_no_reminder(self, app, db, make_event, make_team):
        from quiz_app import db as _db
        from quiz_app.models import RegistrationsEvent
        from quiz_app import scheduler

        with app.app_context():
            today = _dt.datetime.now().date()
            ev = make_event(event_date=_dt.datetime.combine(today, _dt.time(18, 0)))
            team = make_team(name="Confirmed Team")
            reg = RegistrationsEvent(
                team_id=team.id,
                event_id=ev.id,
                status="confirmed",
                waitlist=False,
            )
            _db.session.add(reg)
            _db.session.commit()

            scheduler._app_instance = app

            with patch("quiz_app.scheduler.send_reminder_email") as mock_send:
                scheduler.send_reminders()

            assert mock_send.call_count == 0

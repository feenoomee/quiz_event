"""Tests for waitlist / queue registration when event is full."""
import datetime as _dt

from quiz_app.models import Event


class TestWaitlistRegistration:
    """POST /api/register_team — event full → waitlist entry created."""

    def test_register_when_full_returns_waitlist_true(self, user, make_event, make_team):
        ev = make_event(booked=10, seats=10)
        team = make_team(name="WL Team 1")
        resp = user.post(
            "/api/register_team",
            json={"event_id": ev.id, "team_id": team.id, "player_count": 5},
        )
        data = resp.get_json()
        assert resp.status_code == 201
        assert data["waitlist"] is True

    def test_register_when_full_does_not_increment_booked(self, user, make_event, make_team):
        ev = make_event(booked=10, seats=10)
        team = make_team(name="WL Team 2")
        user.post(
            "/api/register_team",
            json={"event_id": ev.id, "team_id": team.id, "player_count": 5},
        )
        refreshed = Event.query.get(ev.id)
        assert refreshed.booked == 10

    def test_register_when_full_creates_registration_with_waitlist_flag(
        self, user, make_event, make_team
    ):
        from quiz_app.models import RegistrationsEvent
        ev = make_event(booked=10, seats=10)
        team = make_team(name="WL Team 3")
        user.post(
            "/api/register_team",
            json={"event_id": ev.id, "team_id": team.id, "player_count": 5},
        )
        reg = RegistrationsEvent.query.filter_by(event_id=ev.id).first()
        assert reg is not None
        assert reg.waitlist is True

    def test_register_when_spots_available_does_not_set_waitlist(
        self, user, make_event, make_team
    ):
        ev = make_event(booked=5, seats=10)
        team = make_team(name="Normal Team 1")
        resp = user.post(
            "/api/register_team",
            json={"event_id": ev.id, "team_id": team.id, "player_count": 5},
        )
        data = resp.get_json()
        assert resp.status_code == 201
        assert data["waitlist"] is False

    def test_register_when_spots_available_increments_booked(
        self, user, make_event, make_team
    ):
        ev = make_event(booked=5, seats=10)
        team = make_team(name="Normal Team 2")
        user.post(
            "/api/register_team",
            json={"event_id": ev.id, "team_id": team.id, "player_count": 5},
        )
        refreshed = Event.query.get(ev.id)
        assert refreshed.booked == 10


class TestCancelRegistration:
    """DELETE /api/registrations/<id> — check booked decrement."""

    def test_cancel_waitlist_does_not_decrement_booked(
        self, user, make_waitlist_team
    ):
        from quiz_app.models import Event as E
        ev, team, reg = make_waitlist_team()
        resp = user.delete(f"/api/registrations/{reg.id}")
        assert resp.status_code == 200
        refreshed = E.query.get(ev.id)
        assert refreshed.booked == 10

    def test_cancel_regular_decrements_booked(
        self, user, make_event, make_team
    ):
        from quiz_app.models import RegistrationsEvent, Event as E
        ev = make_event(booked=5, seats=10)
        team = make_team(name="Cancel Team")
        user.post(
            "/api/register_team",
            json={"event_id": ev.id, "team_id": team.id, "player_count": 3},
        )
        reg = RegistrationsEvent.query.filter_by(event_id=ev.id).first()
        resp = user.delete(f"/api/registrations/{reg.id}")
        assert resp.status_code == 200
        refreshed = E.query.get(ev.id)
        assert refreshed.booked == 5


class TestAdminEventRegistrations:
    """GET /api/admin/events/<id>/registrations returns waitlist separately."""

    def test_returns_waitlist_key(self, admin_client, make_waitlist_team):
        ev, team, reg = make_waitlist_team()
        resp = admin_client.get(f"/api/admin/events/{ev.id}/registrations")
        data = resp.get_json()
        assert resp.status_code == 200
        assert "waitlist" in data
        assert "registrations" in data

    def test_waitlist_contains_team(self, admin_client, make_waitlist_team):
        ev, team, reg = make_waitlist_team()
        resp = admin_client.get(f"/api/admin/events/{ev.id}/registrations")
        data = resp.get_json()
        wl_ids = [r["team_id"] for r in data["waitlist"]]
        assert team.id in wl_ids

    def test_waitlist_includes_captain_info(
        self, admin_client, make_waitlist_team
    ):
        ev, team, reg = make_waitlist_team()
        resp = admin_client.get(f"/api/admin/events/{ev.id}/registrations")
        data = resp.get_json()
        wl = next(r for r in data["waitlist"] if r["team_id"] == team.id)
        assert "captain" in wl
        assert wl["captain"]["name"] == "U S"
        assert wl["captain"]["email"] == "test@example.com"


class TestAdminConfirmWaitlist:
    """POST /api/admin/registrations/<id>/confirm-waitlist — moves team to confirmed."""

    def test_confirm_waitlist_sets_waitlist_false(self, admin_client, make_waitlist_team):
        from quiz_app.models import RegistrationsEvent
        ev, team, reg = make_waitlist_team()
        resp = admin_client.post(
            f"/api/admin/registrations/{reg.id}/confirm-waitlist",
        )
        assert resp.status_code == 200
        refreshed = RegistrationsEvent.query.get(reg.id)
        assert refreshed.waitlist is False
        assert refreshed.status == "confirmed"

    def test_confirm_waitlist_increments_booked(self, admin_client, make_waitlist_team):
        from quiz_app.models import Event as E
        ev, team, reg = make_waitlist_team()
        admin_client.post(
            f"/api/admin/registrations/{reg.id}/confirm-waitlist",
        )
        refreshed = E.query.get(ev.id)
        assert refreshed.booked == 15


class TestAutoCleanupPendingWaitlist:
    """auto_cleanup_pending must NOT remove waitlist entries."""

    def test_waitlist_pending_survives_cleanup(self, app, db, make_waitlist_team):
        from quiz_app.models import RegistrationsEvent
        with app.app_context():
            from quiz_app.blueptints.api import auto_cleanup_pending
            ev, team, reg = make_waitlist_team()
            auto_cleanup_pending()
            survives = RegistrationsEvent.query.get(reg.id)
            assert survives is not None

    def test_non_waitlist_pending_gets_cleaned(self, app, db, user, make_event, make_team):
        from quiz_app.models import RegistrationsEvent
        with app.app_context():
            from quiz_app import db as _db
            from quiz_app.blueptints.api import auto_cleanup_pending
            ev = make_event(booked=1, seats=10,
                            event_date=_dt.datetime.now() - _dt.timedelta(days=1))
            team = make_team(name="Clean Team")
            reg = RegistrationsEvent(
                team_id=team.id, event_id=ev.id,
                status="pending", waitlist=False,
            )
            _db.session.add(reg)
            _db.session.commit()
            auto_cleanup_pending()
            deleted = RegistrationsEvent.query.get(reg.id)
            assert deleted is None

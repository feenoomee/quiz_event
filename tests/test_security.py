import datetime as dt

import pytest

from quiz_app.helpers import _delete_media_file, _media_file_path
from quiz_app.models import Event, RegistrationsEvent, User


def test_outsider_cannot_join_read_or_cancel(user, db, make_team, make_event):
    team = make_team(captain_email="owner@example.com")
    event = make_event(booked=3)
    reg = RegistrationsEvent(team_id=team.id, event_id=event.id, player_count=3)
    db.session.add(reg)
    db.session.commit()
    outsider = User.query.filter_by(email="test@example.com").one()
    for payload in (None, {"user_id": outsider.id}):
        assert user.post(f"/api/teams/{team.id}/join", json=payload).status_code == 403
    assert outsider not in team.members
    assert user.get("/api/my/registrations").get_json() == []
    assert user.delete(f"/api/registrations/{reg.id}").status_code == 403
    assert user.post(f"/api/registrations/{reg.id}/confirm").status_code == 403
    assert db.session.get(RegistrationsEvent, reg.id) is not None
    assert event.booked == 3


def test_member_cannot_manage_registration(user, db, make_team, make_event):
    team = make_team(captain_email="owner@example.com")
    member = User.query.filter_by(email="test@example.com").one()
    team.members.append(member)
    event = make_event()
    reg = RegistrationsEvent(team_id=team.id, event_id=event.id, player_count=2)
    db.session.add(reg)
    db.session.commit()
    assert user.post("/api/register_team", json={"team_id": team.id, "event_id": event.id}).status_code == 403
    assert user.post(f"/api/registrations/{reg.id}/confirm").status_code == 403
    assert user.delete(f"/api/registrations/{reg.id}").status_code == 403
    assert user.post(f"/api/teams/{team.id}/join", json={"user_id": member.id}).status_code == 403


def test_captain_adds_member_and_manages_registration(user, db, make_team, make_event):
    team = make_team()
    other = make_team(captain_email="member@example.com")
    assert user.post(f"/api/teams/{team.id}/join", json={"user_id": other.user_id}).status_code == 200
    assert user.post(f"/api/teams/{team.id}/join", json={"user_id": other.user_id}).status_code == 409
    event = make_event()
    assert user.post("/api/register_team", json={"team_id": team.id, "event_id": event.id, "player_count": 2}).status_code == 201
    reg = RegistrationsEvent.query.filter_by(team_id=team.id, event_id=event.id).one()
    assert user.post(f"/api/registrations/{reg.id}/confirm").status_code == 200
    assert user.delete(f"/api/registrations/{reg.id}").status_code == 200
    assert event.booked == 0


def test_admin_can_manage_team(admin_client, db, make_team, make_event):
    team = make_team()
    other = make_team(captain_email="member@example.com")
    assert admin_client.post(f"/api/teams/{team.id}/join", json={"user_id": other.user_id}).status_code == 200
    event = make_event()
    assert admin_client.post("/api/register_team", json={"team_id": team.id, "event_id": event.id}).status_code == 201
    reg = RegistrationsEvent.query.filter_by(team_id=team.id, event_id=event.id).one()
    assert admin_client.post(f"/api/registrations/{reg.id}/confirm").status_code == 200
    assert admin_client.delete(f"/api/registrations/{reg.id}").status_code == 200


@pytest.mark.parametrize("path", [
    "../sentinel.txt", "/tmp/sentinel.txt", "C:/sentinel.txt",
    "uploads/events/../../sentinel.txt", "uploads/results/../../sentinel.txt",
    "uploads/events/..\\..\\sentinel.txt", "uploads/avatars/sentinel.txt",
    "uploads/events/missing.webp", "uploads/events/", "uploads/events/..", 123,
])
def test_photo_input_rejects_unsafe_paths(app, admin_client, make_event, tmp_path, monkeypatch, path):
    monkeypatch.setitem(app.config, "UPLOAD_FOLDER", str(tmp_path / "uploads"))
    event = make_event()
    assert admin_client.put(f"/api/events/{event.id}", json={"photo_path": path}).status_code == 400
    assert admin_client.post(f"/api/admin/games/{event.id}/result-photo", json={"result_photo_path": path}).status_code == 400
    response = admin_client.post("/api/events", json={
        "title": "Test", "category": "classic", "date": "2030-01-01", "time": "18:00",
        "location": "Club", "photo_path": path,
    })
    assert response.status_code == 400
    assert event.photo is None


@pytest.mark.parametrize("operation", ["delete", "public_cleanup", "history", "scheduler", "result", "avatar", "poster"])
def test_legacy_paths_never_delete_outside_uploads(app, db, admin_client, make_event, tmp_path, monkeypatch, operation):
    from quiz_app.models import SitePoster
    from quiz_app import scheduler
    monkeypatch.setattr(app, "root_path", str(tmp_path))
    monkeypatch.setitem(app.config, "UPLOAD_FOLDER", str(tmp_path / "media" / "uploads"))
    (tmp_path / "media").mkdir()
    sentinel = tmp_path / "sentinel.txt"
    sentinel.write_text("keep", encoding="utf-8")
    event = make_event(event_date=dt.datetime.now() - dt.timedelta(days=200))
    event.photo = "../sentinel.txt"
    event.result_photo = "../sentinel.txt"
    admin = User.query.filter_by(email="admin@test.com").one()
    admin.avatar = "../sentinel.txt"
    db.session.add(SitePoster(photo="../sentinel.txt"))
    db.session.commit()
    if operation == "delete":
        assert admin_client.delete(f"/api/events/{event.id}").status_code == 200
    elif operation == "public_cleanup":
        assert admin_client.get("/api/events").status_code == 200
    elif operation == "history":
        assert admin_client.post("/api/admin/history/clear").status_code == 200
    elif operation == "scheduler":
        monkeypatch.setattr(scheduler, "_app_instance", app)
        scheduler.cleanup_old_events()
    elif operation == "result":
        assert admin_client.delete(f"/api/admin/games/{event.id}/result-photo").status_code == 200
    elif operation == "avatar":
        assert admin_client.delete("/api/upload/avatar").status_code == 200
    else:
        assert admin_client.delete("/api/poster").status_code == 200
    assert sentinel.read_text(encoding="utf-8") == "keep"


def test_valid_files_and_wrong_category(app, admin_client, make_event, tmp_path, monkeypatch):
    monkeypatch.setitem(app.config, "UPLOAD_FOLDER", str(tmp_path))
    (tmp_path / "events").mkdir()
    photo = tmp_path / "events" / "photo.webp"
    photo.write_bytes(b"test")
    event = make_event()
    assert admin_client.put(f"/api/events/{event.id}", json={"photo_path": "uploads/events/photo.webp"}).status_code == 200
    _delete_media_file("uploads/events/photo.webp", "results")
    assert photo.exists()
    assert admin_client.delete(f"/api/events/{event.id}").status_code == 200
    assert not photo.exists()


def test_symlink_cannot_escape_uploads(app, tmp_path, monkeypatch):
    monkeypatch.setitem(app.config, "UPLOAD_FOLDER", str(tmp_path / "uploads"))
    folder = tmp_path / "uploads" / "events"
    folder.mkdir(parents=True)
    sentinel = tmp_path / "sentinel.txt"
    sentinel.write_text("keep", encoding="utf-8")
    try:
        (folder / "link.webp").symlink_to(sentinel)
    except OSError:
        pytest.skip("Creating symlinks is not permitted on this system")
    assert _media_file_path("uploads/events/link.webp", "events") is None
    _delete_media_file("uploads/events/link.webp", "events")
    assert sentinel.exists()

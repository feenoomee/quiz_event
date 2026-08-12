import datetime as dt
from io import BytesIO

from PIL import Image

from quiz_app.models import Event, RegistrationsEvent, Team


def _image_file(size=(2560, 1440), fmt="PNG"):
    bio = BytesIO()
    Image.new("RGB", size, color=(240, 200, 40)).save(bio, format=fmt)
    bio.seek(0)
    return bio


def test_upload_result_photo_accepts_any_size(app, admin_client, tmp_path, monkeypatch):
    monkeypatch.setitem(app.config, "UPLOAD_FOLDER", str(tmp_path))

    small = admin_client.post(
        "/api/upload/result-photo",
        data={"file": (_image_file((1280, 720)), "small.png")},
        content_type="multipart/form-data",
    )
    assert small.status_code == 200
    assert small.get_json()["path"].startswith("uploads/results/")

    large = admin_client.post(
        "/api/upload/result-photo",
        data={"file": (_image_file((4096, 2304)), "large.png")},
        content_type="multipart/form-data",
    )
    assert large.status_code == 200
    assert large.get_json()["path"].startswith("uploads/results/")

    valid = admin_client.post(
        "/api/upload/result-photo",
        data={"file": (_image_file(), "result.png")},
        content_type="multipart/form-data",
    )
    data = valid.get_json()
    assert valid.status_code == 200
    assert data["status"] == "success"
    assert data["path"].startswith("uploads/results/")


def test_upload_result_photo_rejects_non_image(app, admin_client, tmp_path, monkeypatch):
    monkeypatch.setitem(app.config, "UPLOAD_FOLDER", str(tmp_path))

    resp = admin_client.post(
        "/api/upload/result-photo",
        data={"file": (BytesIO(b"not an image at all"), "fake.png")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 400


def test_saving_result_photo_clears_scores(app, db, admin_client):
    event = Event(
        name="Past game",
        description="Test",
        category="5x5",
        date=dt.datetime.now() - dt.timedelta(days=1),
        location="Club",
        seats=10,
        price=500,
        scores="[[1, 2, 3]]",
    )
    db.session.add(event)
    db.session.commit()

    resp = admin_client.post(
        f"/api/admin/games/{event.id}/result-photo",
        json={"result_photo_path": "uploads/results/result.png"},
    )
    assert resp.status_code == 200

    saved = db.session.get(Event, event.id)
    assert saved.result_photo == "uploads/results/result.png"
    assert saved.scores is None


def test_saving_scoreboard_clears_result_photo(app, db, admin_client):
    event = Event(
        name="Past game",
        description="Test",
        category="5x5",
        date=dt.datetime.now() - dt.timedelta(days=1),
        location="Club",
        seats=10,
        price=500,
        rounds=2,
        result_photo="uploads/results/result.png",
    )
    team = Team(name="Team A", user_id=1)
    db.session.add_all([event, team])
    db.session.flush()
    db.session.add(RegistrationsEvent(team_id=team.id, event_id=event.id, player_count=5))
    db.session.commit()

    resp = admin_client.post(
        f"/api/admin/games/{event.id}/scoreboard",
        json={"scores": [[4, 5]]},
    )
    assert resp.status_code == 200

    saved = db.session.get(Event, event.id)
    assert saved.result_photo is None
    assert saved.get_scores() == [[4, 5]]


def test_public_past_games_returns_photo_result(db, admin_client):
    event = Event(
        name="Past game",
        description="Test",
        category="5x5",
        date=dt.datetime.now() - dt.timedelta(days=1),
        location="Club",
        seats=10,
        price=500,
        result_photo="uploads/results/result.png",
    )
    db.session.add(event)
    db.session.commit()

    resp = admin_client.get("/api/games/past")
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["games"][0]["result_type"] == "photo"
    assert data["games"][0]["result_photo"].endswith("/media/uploads/results/result.png")
    assert data["games"][0]["results"] == []


def test_public_past_games_includes_future_game_with_photo(db, admin_client):
    event = Event(
        name="Future game",
        description="Test",
        category="5x5",
        date=dt.datetime.now() + dt.timedelta(days=3),
        location="Club",
        seats=10,
        price=500,
        result_photo="uploads/results/result.png",
    )
    db.session.add(event)
    db.session.commit()

    resp = admin_client.get("/api/games/past")
    data = resp.get_json()
    assert resp.status_code == 200
    ids = [g["id"] for g in data["games"]]
    assert event.id in ids
    game = next(g for g in data["games"] if g["id"] == event.id)
    assert game["result_type"] == "photo"

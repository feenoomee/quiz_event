from io import BytesIO

from PIL import Image

from quiz_app.models import SitePoster


def _image_file(size=(800, 1200), fmt="PNG"):
    bio = BytesIO()
    Image.new("RGB", size, color=(240, 200, 40)).save(bio, format=fmt)
    bio.seek(0)
    return bio


def test_poster_requires_admin(user):
    resp = user.post(
        "/api/poster",
        data={"file": (_image_file(), "poster.png")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 403


def test_upload_replace_and_delete_poster(app, db, admin_client, tmp_path, monkeypatch):
    monkeypatch.setitem(app.config, "UPLOAD_FOLDER", str(tmp_path))

    empty = admin_client.get("/api/poster")
    assert empty.status_code == 200
    assert empty.get_json()["url"] is None

    first = admin_client.post(
        "/api/poster",
        data={"file": (_image_file(), "august.png")},
        content_type="multipart/form-data",
    )
    assert first.status_code == 200
    data = first.get_json()
    assert data["photo"].startswith("uploads/calendar/")
    assert SitePoster.current().photo == data["photo"]

    second = admin_client.post(
        "/api/poster",
        data={"file": (_image_file((600, 900)), "september.png")},
        content_type="multipart/form-data",
    )
    assert second.status_code == 200
    assert SitePoster.query.count() == 1
    assert SitePoster.current().photo == second.get_json()["photo"]
    assert SitePoster.current().photo != data["photo"]

    deleted = admin_client.delete("/api/poster")
    assert deleted.status_code == 200
    assert SitePoster.current() is None


def test_index_shows_poster_and_nearest_quiz(app, db, client):
    import datetime as dt
    from quiz_app.models import Event

    event = Event(
        name="Nearest quiz",
        description="Soon",
        category="classic",
        date=dt.datetime.now() + dt.timedelta(days=2),
        location="Club",
        seats=10,
        price=500,
    )
    db.session.add(event)
    db.session.add(SitePoster(photo="uploads/calendar/afisha.webp"))
    db.session.commit()

    html = client.get("/").get_data(as_text=True)
    assert "Ближайший квиз" in html
    assert "Афиша месяца" in html
    assert "hero-poster-btn" in html
    assert "uploads/calendar/afisha.webp" in html

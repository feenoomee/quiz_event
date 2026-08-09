"""Tests for admin role management endpoints (grant / revoke by email)."""
from werkzeug.security import generate_password_hash

from quiz_app.models import User


def _mk_user(db, email, role="user"):
    user = User(
        first_name="U",
        second_name="S",
        email=email,
        number_telephone="+79000000000",
        password_hash=generate_password_hash("pass123"),
        role=role,
    )
    db.session.add(user)
    db.session.flush()
    return user


class TestAdminGrantRole:
    """POST /api/admin/users/role — grant admin status by email."""

    def test_grant_admin_by_email(self, app, db, admin_client):
        _mk_user(db, "test@example.com", role="user")
        db.session.commit()

        resp = admin_client.post(
            "/api/admin/users/role",
            json={"email": "test@example.com", "role": "admin"},
        )
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["status"] == "success"
        with app.app_context():
            u = User.query.filter_by(email="test@example.com").first()
            assert u.role == "admin"

    def test_grant_to_missing_user_returns_404(self, admin_client):
        resp = admin_client.post(
            "/api/admin/users/role",
            json={"email": "nobody@example.com", "role": "admin"},
        )
        assert resp.status_code == 404

    def test_revoke_admin(self, app, db, admin_client):
        resp = admin_client.post(
            "/api/admin/users/role",
            json={"email": "admin@test.com", "role": "user"},
        )
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["status"] == "success"
        with app.app_context():
            u = User.query.filter_by(email="admin@test.com").first()
            assert u.role == "user"

    def test_requires_admin(self, app, db):
        _mk_user(db, "test@example.com", role="user")
        db.session.commit()
        c = app.test_client()
        c.post(
            "/api/login",
            json={"email": "test@example.com", "password": "pass123"},
        )
        resp = c.post(
            "/api/admin/users/role",
            json={"email": "test@example.com", "role": "admin"},
        )
        assert resp.status_code == 403

    def test_invalid_role_rejected(self, admin_client):
        resp = admin_client.post(
            "/api/admin/users/role",
            json={"email": "admin@test.com", "role": "superuser"},
        )
        assert resp.status_code == 400


class TestAdminListAdmins:
    """GET /api/admin/users/admins returns the admin list."""

    def test_lists_admins(self, admin_client):
        resp = admin_client.get("/api/admin/users/admins")
        assert resp.status_code == 200
        data = resp.get_json()
        assert any(u["email"] == "admin@test.com" for u in data)

    def test_requires_admin(self, app, db):
        _mk_user(db, "test@example.com", role="user")
        db.session.commit()
        c = app.test_client()
        c.post(
            "/api/login",
            json={"email": "test@example.com", "password": "pass123"},
        )
        resp = c.get("/api/admin/users/admins")
        assert resp.status_code == 403

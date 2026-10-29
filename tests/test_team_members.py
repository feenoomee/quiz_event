import pytest

from quiz_app.models import RegistrationsEvent, User


def test_captain_adds_by_email(user, db, make_team, make_event):
    team = make_team()
    member_team = make_team(captain_email="member@example.com")
    event = make_event(booked=2)
    reg = RegistrationsEvent(team_id=team.id, event_id=event.id, player_count=2)
    db.session.add(reg)
    db.session.commit()
    response = user.post(f"/api/teams/{team.id}/join", json={"email": "  MEMBER@EXAMPLE.COM  "})
    assert response.status_code == 200
    member = db.session.get(User, member_team.user_id)
    assert response.json["member"] == {"id": member.id, "name": member.name}
    assert member in team.members
    assert reg.player_count == 2
    assert event.booked == 2
    own = next(t for t in user.get("/api/my/teams").json if t["id"] == team.id)
    assert own["can_manage"] is True
    assert member.id in [m["id"] for m in own["members"]]
    # The added player sees the team and its game but cannot manage either.
    member_client = user.application.test_client()
    member_client.post("/api/login", json={"email": member.email, "password": "pass123"})
    visible = next(t for t in member_client.get("/api/my/teams").json if t["id"] == team.id)
    assert visible["can_manage"] is False
    registration = next(r for r in member_client.get("/api/my/registrations").json if r["id"] == reg.id)
    assert registration["can_manage"] is False


def test_duplicate_member_is_not_added_twice(user, db, make_team):
    team = make_team()
    member_team = make_team(captain_email="member@example.com")
    url = f"/api/teams/{team.id}/join"
    assert user.post(url, json={"email": "member@example.com"}).status_code == 200
    assert user.post(url, json={"email": "MEMBER@example.com"}).status_code == 409
    assert len(team.members) == 2


def test_unknown_email_leaves_team_unchanged(user, make_team):
    team = make_team()
    response = user.post(f"/api/teams/{team.id}/join", json={"email": "unknown@example.com"})
    assert response.status_code == 404
    assert "зарегистрироваться" in response.json["message"]
    assert len(team.members) == 1


@pytest.mark.parametrize("payload", [None, [], "email", {}, {"email": None}, {"email": []}, {"email": ""}, {"email": "bad"}, {"email": "@example.com"}, {"email": "a@"}, {"email": "a b@example.com"}, {"email": "a" * 121 + "@example.com"}])
def test_invalid_member_payload_returns_400(user, make_team, payload):
    team = make_team()
    assert user.post(f"/api/teams/{team.id}/join", json=payload).status_code == 400
    assert len(team.members) == 1


def test_outsider_cannot_add_by_email(user, make_team):
    team = make_team(captain_email="owner@example.com")
    for email in ("test@example.com", "unknown@example.com"):
        assert user.post(f"/api/teams/{team.id}/join", json={"email": email}).status_code == 403
    assert len(team.members) == 1


def test_admin_adds_by_email(admin_client, make_team):
    team = make_team()
    make_team(captain_email="member@example.com")
    assert admin_client.post(f"/api/teams/{team.id}/join", json={"email": "member@example.com"}).status_code == 200


def test_anonymous_cannot_add(client, make_team):
    team = make_team()
    response = client.post(f"/api/teams/{team.id}/join", json={"email": "test@example.com"})
    assert response.status_code in (302, 401)
    assert len(team.members) == 1

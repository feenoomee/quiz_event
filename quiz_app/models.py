import json
import secrets
from datetime import datetime, timedelta

from . import db
from flask_login import UserMixin
from sqlalchemy_utils import PhoneNumberType
from werkzeug.security import generate_password_hash, check_password_hash


team_members = db.Table(
    "team_members",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("team_id", db.Integer, db.ForeignKey("teams.id"), primary_key=True),
)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    second_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    password_hash = db.Column(db.String(255), nullable=False)
    number_telephone = db.Column(PhoneNumberType(), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    avatar = db.Column(db.String(255), nullable=True)

    teams = db.relationship("Team", secondary=team_members, back_populates="members")
    owned_teams = db.relationship("Team", backref="captain", foreign_keys="Team.user_id")

    @property
    def name(self):
        return f"{self.first_name} {self.second_name}".strip()

    @property
    def short_name(self):
        if self.first_name and self.second_name:
            return f"{self.second_name} {self.first_name[0]}."
        return self.name or "Кабинет"

    @property
    def password(self):
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, raw_password):
        self.set_password(raw_password)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self):
        return f"<User {self.email}>"


class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(120), nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False, default=0)
    booked = db.Column(db.Integer, nullable=False, default=0)
    tag = db.Column(db.String(20), nullable=True)
    photo = db.Column(db.String(255), nullable=True)
    rounds = db.Column(db.Integer, nullable=False, default=7)
    scores = db.Column(db.Text, nullable=True)
    result_photo = db.Column(db.String(255), nullable=True)

    registrations = db.relationship("RegistrationsEvent", back_populates="event", cascade="all, delete-orphan")

    def get_scores(self):
        if not self.scores:
            return []
        try:
            return json.loads(self.scores)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_scores(self, scores_data):
        self.scores = json.dumps(scores_data)


class RegistrationsEvent(db.Model):
    __tablename__ = "registrations"

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    player_count = db.Column(db.Integer, nullable=False, default=1)
    comment = db.Column(db.String(500), nullable=True)
    registered_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.String(20), default="pending")
    waitlist = db.Column(db.Boolean, default=False)
    reminder_sent_at = db.Column(db.DateTime, nullable=True)

    event = db.relationship("Event", back_populates="registrations")
    team = db.relationship("Team", back_populates="registrations")


class Team(db.Model):
    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    members = db.relationship("User", secondary=team_members, back_populates="teams")
    registrations = db.relationship("RegistrationsEvent", back_populates="team", cascade="all, delete-orphan")


class PasswordReset(db.Model):
    __tablename__ = "password_resets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)

    user = db.relationship("User", backref="password_resets")

    @staticmethod
    def generate_code():
        return f"{secrets.randbelow(10**6):06d}"

    def is_expired(self):
        return datetime.now() > self.expires_at

    @staticmethod
    def create_for_user(user):
        old = PasswordReset.query.filter_by(user_id=user.id, used=False).all()
        for r in old:
            r.used = True
        db.session.flush()

        code = PasswordReset.generate_code()
        reset = PasswordReset(
            user_id=user.id,
            code=code,
            expires_at=datetime.now() + timedelta(minutes=15),
        )
        db.session.add(reset)
        db.session.commit()
        return code


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    token = db.Column(db.String(64), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)

    user = db.relationship("User")

    def is_expired(self):
        return datetime.now() > self.expires_at

    @staticmethod
    def create_for_user(user, token):
        old = PasswordResetToken.query.filter_by(user_id=user.id, used=False).all()
        for r in old:
            r.used = True
        db.session.flush()

        obj = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=datetime.now() + timedelta(minutes=15),
        )
        db.session.add(obj)
        db.session.commit()
        return obj

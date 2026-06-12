from datetime import datetime

from . import db
from flask_login import UserMixin
from sqlalchemy_utils import PhoneNumberType
from werkzeug.security import generate_password_hash, check_password_hash


class User( UserMixin, db.Model ):
    __tablename__ = "users"

    id = db.Column( db.Integer, primary_key = True )
    first_name = db.Column( db.String( 120 ), nullable = False )
    second_name = db.Column( db.String( 120 ), nullable = False )
    email = db.Column( db.String( 120 ), unique = True, nullable = False )
    role = db.Column( db.String( 20 ), nullable = False, default = "user" )
    password_hash = db.Column( db.String( 255 ), nullable = False )
    number_telephone = db.Column( PhoneNumberType(), nullable = False )
    created_at = db.Column( db.DateTime, nullable = False, server_default=db.func.now() )
    avatar = db.Column( db.String( 255 ), nullable=True )

    # Хеширование пароля
    @property
    def name( self ):
        return f"{self.first_name} {self.second_name}".strip()

    @property
    def short_name( self ):
        if self.first_name and self.second_name:
            return f"{self.second_name} {self.first_name[0]}."
        return self.name or "Кабинет"

    @property
    def password( self ):
        raise AttributeError( "Password is write-only." )

    @password.setter
    def password( self, raw_password ):
        self.set_password( raw_password )

    def set_password( self, raw_password ):
        self.password_hash = generate_password_hash( raw_password )

    def check_password( self, raw_password ):
        return check_password_hash( self.password_hash, raw_password )

    def __repr__( self ):
        return f"<User {self.email}>"

class Event( db.Model ):
    __tablename__ = "events"
    id = db.Column( db.Integer, primary_key = True )
    name = db.Column( db.String( 120 ), nullable = False )
    description = db.Column( db.String( 255 ), nullable = False )
    category = db.Column( db.String( 120 ), nullable = False )
    date = db.Column( db.DateTime, nullable = False )
    time = db.Column( db.DateTime, nullable = False )
    location = db.Column( db.String( 120 ), nullable = False )
    seats = db.Column( db.Integer, nullable = False )
    price = db.Column( db.Integer, nullable = False, default = 0 )
    booked = db.Column( db.Integer, nullable = False, default = 0 )
    tag = db.Column( db.String( 20 ), nullable = True )
    photo = db.Column( db.String( 255 ), nullable=True )

class RegistrationsEvent( db.Model ):
    __tablename__ = "registrations"

    id = db.Column( db.Integer, primary_key = True )
    team_id = db.Column( db.Integer, db.ForeignKey( "teams.id" ), nullable = False )
    event_id = db.Column( db.Integer, db.ForeignKey( "events.id" ), nullable = False )
    registered_at = db.Column( db.DateTime, nullable = False )
    status = db.Column( db.String( 20 ), default = "registered" )

class Team( db.Model ):
    __tablename__ = "teams"

    id = db.Column( db.Integer, primary_key = True )
    name = db.Column( db.String( 120 ), nullable = False )
    user_id = db.Column( db.Integer, db.ForeignKey( "users.id" ), nullable = False )

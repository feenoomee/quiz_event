from . import db
from sqlalchemy_utils import PhoneNumberType


class User( db.Model ):
    __tablename__ = "users"

    id = db.Column( db.Integer, primary_key = True )
    name = db.Column( db.String( 120 ), nullable = False )
    email = db.Column( db.String( 120 ), unique = True, nullable = False )
    role = db.Column( db.String( 20 ), nullable = False, default = "user" )
    password = db.Column( db.String( 120 ), nullable = False )
    number_telephone = db.Column( PhoneNumberType(), nullable = False )

    def __repr__( self ):
        return f"<User {self.email}>"


class Event( db.Model ):
    __tablename__ = "events"
    id = db.Column( db.Integer, primary_key = True )
    name = db.Column( db.String( 120 ), nullable = False )
    description = db.Column( db.String( 120 ), nullable = False )


class Registrations( db.Model ):
    __tablename__ = "registrations"

    id = db.Column( db.Integer, primary_key = True )

    user_id = db.Column( db.Integer, db.ForeignKey( "users.id" ), nullable = False )

    event_id = db.Column( db.Integer, db.ForeignKey( "events.id" ), nullable = False )

    registered_at = db.Column( db.DateTime, nullable = False )

    status = db.Column( db.String( 20 ), default = "registered" )

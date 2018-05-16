from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(40))
    last_name = db.Column(db.String(40))
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'))
    profile = db.relationship('Profile')
    entries_added = db.relationship('History', backref='author', lazy='dynamic')
       
    def __repr__(self):
        return 'User(first_name="{}",last_name="{}",email="{}")'.format(self.first_name,
                       self.last_name,self.email)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    description = db.Column(db.String(200))
    def __repr__(self):
        return 'Profile(name="{}",description="{}")'.format(self.name,
                       self.description)
    
class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id =  db.Column(db.Integer, db.ForeignKey('user.id'))
    operation = db.Column(db.String(20))
    description = db.Column(db.String(200))   
    def __repr__(self):
        return 'History(user="{}",operation="{}", description="{}")'.format(self.author.email,
                       self.operation,self.description)    

class InstrumentType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    instruments = db.relationship('Instrument',backref='instrument_type')
    def __repr__(self):
        return 'InstrumentType(name="{}")'.format(self.name)

class Instrument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    instrument_type_id = db.Column(db.Integer, db.ForeignKey('instrument_type.id'))
    activities = db.relationship('Activity',backref='instrument')
    def __repr__(self):
        return 'Instrument(name="{}",type={})'.format(self.name,self.instrument_type.name)
    
class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))
    locations = db.relationship('Location', backref='city', lazy='dynamic')
    def __repr__(self):
        return 'City(name="{}"'.format(self.name)   

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(65)) 
    additional_info = db.Column(db.String(1000))
    events = db.relationship('Event', backref='organization', lazy='dynamic') 
    def __repr__(self):
        return 'Organization(name="{}"'.format(self.name)   

class EventType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20)) 
    description = db.Column(db.String(200))
    events = db.relationship('Event', backref='event_type', lazy='dynamic') 
    def __repr__(self):
        return 'EventType(name="{}"'.format(self.name)   
        
class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))
    def __repr__(self):
        return 'Country(name="{}"'.format(self.name)   
        
class PremiereType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))    
    musical_pieces = db.relationship('MusicalPiece', backref='premier_type', lazy='dynamic')
    def __repr__(self):
        return 'PremiereType(name="{}"'.format(self.name)   
        
nationality = db.Table('nationality', 
    db.Column('person_id', db.Integer, db.ForeignKey('person.id')),
    db.Column('country_id', db.Integer, db.ForeignKey('country.id'))
) 
        
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(40))
    last_name = db.Column(db.String(40))
    birth_date = db.Column(db.Date)
    death_date = db.Column(db.Date)    
    biography = db.Column(db.String(2000))    
    musical_pieces = db.relationship('MusicalPiece', backref='author', lazy='dynamic') 
    participations = db.relationship('Participant', backref='person', lazy='dynamic')
    nationalities  = db.relationship('Country',
                    secondary=nationality,
                    backref='persons')    
    def __repr__(self):
        return 'Person(first_name="{}",last_name="{}"'.format(self.first_name,self.last_name)

class MediaLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mime_type = db.Column(db.String(20))
    link = db.Column(db.String(200))
    description = db.Column(db.String(150))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))   
    def __repr__(self):
        return 'MediaLink(mime_type="{}",link="{}"'.format(self.mime_type,self.location)    

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20)) 
    instrument_id = db.Column(db.Integer, db.ForeignKey('instrument.id'))   
    participants = db.relationship('Participant', backref='activity', lazy='dynamic')
    def __repr__(self):
        return 'Activity(name="{}",instrument="{}"'.format(self.name,self.instrument.name)        
    

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))    
    address = db.Column(db.String(200))    
    additional_info = db.Column(db.String(300))
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    events = db.relationship('Event', backref='location', lazy='dynamic') 
    def __repr__(self):
        return 'Location(name="{}",address="{}",city_id="{}"'.format(self.name,self.address,self.city_id)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)                
    name = db.Column(db.String(120))  
    date = db.Column(db.Date)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'))
    information = db.Column(db.String(600))  
    event_type_id = db.Column(db.Integer, db.ForeignKey('event_type.id'))
    participants = db.relationship('Participant', backref='event', lazy='dynamic')
    media = db.relationship('MediaLink', backref='event', lazy='dynamic')
    def __repr__(self):
        return 'Event(name="{}",date="{}",city_id="{}"'.format(self.name,self.date)


class MusicalPiece(db.Model):
    id = db.Column(db.Integer, primary_key=True)                
    name = db.Column(db.String(100))
    creation_date = db.Column(db.Date)
    author_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    premiere_type_id = db.Column(db.Integer, db.ForeignKey('premiere_type.id'))
    def __repr__(self):
        return 'MusicalPiece(name="{}",creation_date="{}",author_id="{},premiere_type_id={}"'.format(self.name,self.creation_date,self.author_id,self.premiere_type_id) 


player = db.Table('player', 
    db.Column('participant_id', db.Integer, db.ForeignKey('participant.id')),
    db.Column('musical_piece_id', db.Integer, db.ForeignKey('musical_piece.id'))
)      

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))  
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))      
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'))      
    children = db.relationship("MusicalPiece",
                    secondary=player,
                    backref="participants")          
    def __repr__(self):
        return 'Participant(person="{}",event="{}",activity="{}'.format(self.person,self.event,self.activity)


    

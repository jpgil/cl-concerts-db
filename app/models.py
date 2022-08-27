from time import time
from datetime import datetime
import calendar
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'))
    entries_added = db.relationship('History', backref='user', lazy='dynamic')
       
    def __repr__(self):
        return 'User(first_name="{}",last_name="{}",email="{}")'.format(self.first_name,
                       self.last_name,self.email)
    def get_full_name(self):
        return '{}, {}'.format(self.last_name,self.first_name) if self.last_name else self.first_name
    
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
    name = db.Column(db.String(80))
    description = db.Column(db.String(200))
    users = db.relationship('User',backref='profile')
    def __repr__(self):
        return 'Profile(name="{}",description="{}")'.format(self.name,
                       self.description)
    
class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id =  db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime)
    operation = db.Column(db.String(80))
    description = db.Column(db.String(200))   
    def __repr__(self):
        return 'History(user="{}",datetime={}, operation="{}", description="{}")'.format(self.user.email,
                       self.timestamp,self.operation,self.description)    

class InstrumentType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    instruments = db.relationship('Instrument',backref='instrument_type')
    def get_name(self):
        return self.name
    def __repr__(self):
        return 'InstrumentType(name="{}")'.format(self.name)

class Instrument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    instrument_type_id = db.Column(db.Integer, db.ForeignKey('instrument_type.id'))
    activity = db.relationship("Activity", uselist=False, backref="instrument")
    musical_pieces = db.relationship(
        "MusicalPiece",
        secondary=db.Table('musicalpiece_instrument',
                    db.Column("instrument_id", db.Integer, db.ForeignKey('instrument.id'),
                                primary_key=True),
                    db.Column("musical_piece_id", db.Integer, db.ForeignKey('musical_piece.id'),
                                primary_key=True)
                ),
        backref="instruments"
        )    
    def get_name(self):
        if self.instrument_type:
            return "{} ({})".format(self.name,self.instrument_type.name)
        else:
            return self.name
    def __repr__(self):
        return 'Instrument(name="{}",instrument_type={})'.format(self.name,'' if not self.instrument_type else  self.instrument_type.name)
    
class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45))
    locations = db.relationship('Location', backref='city', lazy='dynamic')
    def get_name(self):
        return self.name    
    def __repr__(self):
        return 'City(name="{}")'.format(self.name)   

class Gender(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30)) 
    people = db.relationship('Person', backref='gender')
    def get_name(self):
        return self.name
    def __repr__(self):
        return 'Gender(name="{}")'.format(self.name)
    
class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(65)) 
    additional_info = db.Column(db.String(4000))
    events = db.relationship(
        "Event",
        secondary=db.Table('event_organization',
                    db.Column("organization_id", db.Integer, db.ForeignKey('organization.id'),
                                primary_key=True),
                    db.Column("event_id", db.Integer, db.ForeignKey('event.id'),
                                primary_key=True)
                ),
        backref="organizations"
        )   
    def get_name(self):
        return self.name
    def __repr__(self):
        return 'Organization(name="{}")'.format(self.name)   

class EventType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80)) 
    description = db.Column(db.String(200))
    events = db.relationship('Event', backref='event_type', lazy='dynamic') 
    def get_name(self):
        return self.name
    def __repr__(self):
        return 'EventType(name="{}")'.format(self.name)   

class Cycle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80)) 
    events = db.relationship('Event', backref='cycle', lazy='dynamic') 
    def get_name(self):
        return self.name
    def __repr__(self):
        return 'Cycle(name="{}")'.format(self.name)  
        
class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45))
    def get_name(self):
        return self.name
    def __repr__(self):
        return 'Country(name="{}")'.format(self.name)   
        
class PremiereType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))    
    performances = db.relationship('Performance', backref='premiere_type', lazy='dynamic')
    def get_name(self):
        return self.name
    def __repr__(self):
        return 'PremiereType(name="{}")'.format(self.name)   
        
nationality = db.Table('nationality', 
    db.Column('person_id', db.Integer, db.ForeignKey('person.id')),
    db.Column('country_id', db.Integer, db.ForeignKey('country.id'))
) 


        
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    birth_year = db.Column(db.Integer)
    death_year = db.Column(db.Integer)    
    biography = db.Column(db.String(8000))    
    gender_id = db.Column(db.Integer, db.ForeignKey('gender.id'))
    participants = db.relationship('Participant', backref='person', lazy='dynamic')
    nationalities  = db.relationship('Country',
                    secondary=nationality,
                    backref='people')    
    memberships = db.relationship('MusicalEnsembleMember', backref = 'person', lazy='dynamic')
    bio_person = db.relationship('BioPerson', backref='person', lazy='dynamic', cascade="delete, merge, save-update")
    def __repr__(self):
        return 'Person(first_name="{}",last_name="{}")'.format(self.first_name,self.last_name)
    def get_name(self):
        if self.last_name and self.first_name:
            return '{}, {}'.format(self.last_name,self.first_name) 
        else:
            return self.last_name if self.last_name else self.first_name

    def has_bio(self):
        return self.bio_person.count() == 1
    def get_bio(self):
        return self.bio_person.first()
    
class MediaLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mime_type = db.Column(db.String(80))
    filename = db.Column(db.String(200))
    url = db.Column(db.String(512))
    description = db.Column(db.String(2000))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))   
    def get_name(self):
        return self.filename
    def __repr__(self):
        return 'MediaLink(mime_type="{}",filename="{}")'.format(self.mime_type,self.filename)    

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80)) 
    instrument_id = db.Column(db.Integer, db.ForeignKey('instrument.id'))
    participants = db.relationship('Participant', backref = 'activity', lazy='dynamic')
    musical_ensemble_members = db.relationship('MusicalEnsembleMember', backref = 'activity', lazy='dynamic')    
    def get_name(self):
        if self.instrument:
            return "{} - {}".format(self.name,self.instrument.name)
        else:
            return "{}".format(self.name)
        
    def __repr__(self):
        return 'Activity(name="{}",instrument_id="{}")'.format(self.name,self.instrument_id)        
    

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(85))    
    address = db.Column(db.String(300))    
    additional_info = db.Column(db.String(4000))
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    events = db.relationship('Event', backref='location', lazy='dynamic') 
    def get_name(self):
        return "{}, {}".format(self.name, self.city.name)
    def __repr__(self):
        return 'Location(name="{}",address="{}",city_id="{}")'.format(self.name,self.address,self.city_id)




class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)                
    name = db.Column(db.String(120))  
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    day = db.Column(db.Integer)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    information = db.Column(db.String(4000))  
    sources = db.Column(db.String(2000))  
    event_type_id = db.Column(db.Integer, db.ForeignKey('event_type.id'))
    cycle_id = db.Column(db.Integer, db.ForeignKey('cycle.id'))
    participants = db.relationship('Participant', backref='event', lazy='dynamic')
    performances = db.relationship('Performance', backref='event', lazy='dynamic')
    medialinks = db.relationship('MediaLink', backref='event', lazy='dynamic')     
    def get_string_date(self):
        if (self.year and self.month and self.day):
            return "{:04d}-{:02d}-{:02d}".format(self.year,self.month,self.day)
        elif (self.year and self.month):
            return "{}-{}".format(self.year,self.month)
        elif (self.year):
            return "{}".format(self.year)            
        else:
            return "Sin fecha"
    # since some dates doesn't have month or day, for those we need to be
    # as inclusive as possible, so we'll convert it to the min possible date
    # for comparing the the end_date and to max possible date for comparing with
    # the min. For complete dates min_date == max_date
    def get_dates(self):
        min_date=datetime(self.year,self.month if self.month else 1,self.day if self.day else 1)
        max_month=self.month if self.month else 12
        max_day=self.day if self.day else calendar.monthrange(self.year, max_month)[1]
        max_date=datetime(self.year,max_month,max_day)
        return [min_date,max_date]
    
    def get_name(self):
        return '[{}] {} - {} ({})'.format(self.get_string_date(),self.event_type.name, self.name, self.location.name) if self.name else  '[{}] {} ({})'.format(self.get_string_date(),
                self.event_type.name, self.location.name)
    def __repr__(self):
        return 'Event(name="{}",date="{}",location_id="{}")'.format(self.name,self.get_string_date(),self.location_id)

composer = db.Table('composer',
    db.Column('musical_piece_id', db.Integer, db.ForeignKey('musical_piece.id')),
    db.Column('person_id', db.Integer, db.ForeignKey('person.id'))
)

class MusicalPiece(db.Model):
    id = db.Column(db.Integer, primary_key=True)                
    name = db.Column(db.String(200))
    composition_year = db.Column(db.Integer)
    performances = db.relationship("Performance", backref="musical_piece")
    composers  = db.relationship('Person',
                    secondary=composer,
                    backref='musical_pieces')   
    instrumental_lineup =  db.Column(db.String(200))
    text  = db.Column(db.String(200))
    def get_name(self,clean=False):
        composers_names=""
        for composer in self.composers:
            composers_names+=composer.get_name()+","
        if composers_names != "":
            composers_names=composers_names[:-1] # removes the last ,
        if clean:
            return "{} ({})".format(self.name,composers_names)
        else:
            return "«{}» ({})".format(self.name,composers_names)

    def __repr__(self):
        composers_names=""
        for composer in self.composers:
            composers_names+=composer.get_name()+","
        if composers_names != "":
            composers_names=composers_names[:-1] # removes the last ,
        return 'MusicalPiece(name="{}",composition_year="{}",composers="({})")'.format(self.name,self.composition_year,composers_names) 


class Performance(db.Model):
    id = db.Column(db.Integer, primary_key=True)          
    premiere_type_id = db.Column(db.Integer, db.ForeignKey('premiere_type.id'))
    musical_piece_id =  db.Column(db.Integer, db.ForeignKey('musical_piece.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))     
    def get_name(self):
        return "Evento: {} - Participación: {}".format(self.event.get_name(),self.musical_piece.get_name())
    def __repr__(self):   
        return 'Performance(musical_piece_id="{}", premiere_type_id="{}", event_id"{}")'.format(self.musical_piece_id, self.premiere_type_id, self.event_id)

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))  
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))      
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'))    
    musical_ensemble_id =  db.Column(db.Integer, db.ForeignKey('musical_ensemble.id'))    
    performances = db.relationship(
        "Performance",
        secondary=db.Table('participant_performance',
                    db.Column("participant_id", db.Integer, db.ForeignKey('participant.id'),
                                primary_key=True),
                    db.Column("performance_id", db.Integer, db.ForeignKey('performance.id'),
                                primary_key=True)
                ),
        backref="participants"
        )     
    def get_name(self):
        musical_ensemble_string="[{}] ".format(self.musical_ensemble.name) if self.musical_ensemble else ""
        person_string="{} ".format(self.person.get_name()) if self.person else ""
        activity_string="({})".format(self.activity.name) if self.activity else ""
        return musical_ensemble_string+person_string+activity_string+" "+self.event.get_name()[0:50]
    
    def get_short_name(self):
        musical_ensemble_string="[{}] ".format(self.musical_ensemble.name) if self.musical_ensemble else ""
        person_string="{} ".format(self.person.get_name()) if self.person else ""
        return musical_ensemble_string+person_string
        
    def __repr__(self):
        return 'Participant(person="{}",event="{}",activity="{}")'.format(self.person,self.event,self.activity)

class MusicalEnsembleType(db.Model):
    id = db.Column(db.Integer, primary_key=True)   
    name = db.Column(db.String(100))     
    musical_ensembles = db.relationship('MusicalEnsemble', backref='musical_ensemble_type', lazy='dynamic') 
    def get_name(self):
        return "{}".format(self.name)
    def __repr__(self):
        return 'MusicalPiece(name="{}")'.format(self.name) 

class MusicalEnsemble(db.Model):
    id = db.Column(db.Integer, primary_key=True)   
    name = db.Column(db.String(200))    
    additional_info = db.Column(db.String(4000))
    members = db.relationship('MusicalEnsembleMember', backref='musical_ensemble', lazy='dynamic') 
    musical_ensemble_type_id = db.Column(db.Integer, db.ForeignKey('musical_ensemble_type.id'))    
    participants = db.relationship('Participant', backref='musical_ensemble', lazy='dynamic') 
    bio_musical_ensemble = db.relationship('BioMusicalEnsemble', backref='musical_ensemble', lazy='dynamic', cascade="delete, merge, save-update")

    def get_name(self):
        return "{}".format(self.name)
    def get_short_name(self):
        return "{}".format(self.name)
    def has_bio(self):
        return self.bio_musical_ensemble.count() == 1
    def get_bio(self):
        return self.bio_musical_ensemble.first()        
    def __repr__(self):
        return 'MusicalEnsemble(name="{}")'.format(self.name) 
      

class MusicalEnsembleMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))  
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'))     
    musical_ensemble_id =  db.Column(db.Integer, db.ForeignKey('musical_ensemble.id'))
    def get_name(self):
        if self.activity and self.person:
            return "{} ({}) - {}".format(self.person.get_name(),self.activity.name,self.musical_ensemble.name)
        else:
            return "{} - {}".format(self.person.get_name(),self.musical_ensemble.name) if self.person else "({}) -".format(self.activity.name,self.musical_ensemble.name)

    def __repr__(self):
        str_repr="MusicalEnsembleMember("
        if self.person:
            str_repr+="person='{}' ".format(self.person.get_name())
        if self.activity:
            str_repr+="(activity={}) ".format(self.activity.name)
        str_repr+="musical_ensemble='{}'".format(self.musical_ensemble.name)
        return str_repr



class BioPerson(db.Model):
    """
    Class for Biografias: Persona
    Added in the context of CL3(2022) by jpgil
    Requirements in https://github.com/jpgil/cl-concerts-db/issues/22 
    """
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)  

    # Investigadores del cl-concert-db
    investigacion_autores = db.Column(db.String(800))
    investigacion_fecha = db.Column(db.String(80))
    investigacion_notas = db.Column(db.Text)

    # Datos personales
    # nombre_completo = db.Column(db.String(400))
    # nacimiento = db.Column(db.String(800))
    # fallecimiento = db.Column(db.String(800))
    familia = db.Column(db.Text)
    profesion = db.Column(db.String(400))
    instrumento = db.Column(db.String(2000))
    estudios_formales = db.Column(db.Text)
    estudios_informales = db.Column(db.Text)
    trabajo = db.Column(db.Text)
    ensambles = db.Column(db.Text)
    premios = db.Column(db.Text)
    publicaciones = db.Column(db.Text)

    # Biografia
    biografia = db.Column(db.Text)
    bibliografia = db.Column(db.Text)
    archivos = db.Column(db.Text)
    discografia = db.Column(db.Text)
    links = db.Column(db.Text)
    otros = db.Column(db.Text)

    def get_name(self):
        return "{}".format(self.person.get_name()) if self.person else "ERROR -- person_id is Null"

    def __repr__(self):
        # return 'BioPerson(person_id="{}",name="{}")'.format(self.person.id, self.person.get_name())
        return 'BioPerson(person_id="{}",name="{}",bio="{}")'.format(
            self.person.id, 
            self.person.get_name(),
            self.biografia[:40]
            )

class BioMusicalEnsemble(db.Model):
    """
    Class for Biografias: Ensamble
    Added in the context of CL3(2022) by jpgil
    Requirements in https://github.com/jpgil/cl-concerts-db/issues/22 
    """
    id = db.Column(db.Integer, primary_key=True)
    musical_ensemble_id = db.Column(db.Integer, db.ForeignKey('musical_ensemble.id'), nullable=False)

    # Investigadores del cl-concert-db
    investigacion_autores = db.Column(db.String(800))
    investigacion_fecha = db.Column(db.String(80))
    investigacion_notas = db.Column(db.Text)

    # Datos ensamble
    # nombre_completo = db.Column(db.String(400))
    fundacion = db.Column(db.String(800))
    termino = db.Column(db.String(800))
    integrantes = db.Column(db.String(2000))
    # tipo_ensamble = db.Column(db.String(200))
    repertorio = db.Column(db.Text)
    premios = db.Column(db.Text)
    publicaciones = db.Column(db.Text)

    # Biografia
    biografia = db.Column(db.Text)
    bibliografia = db.Column(db.Text)
    archivos = db.Column(db.Text)
    discografia = db.Column(db.Text)
    links = db.Column(db.Text)
    otros = db.Column(db.Text)

    def get_name(self):
        return "{}".format(self.musical_ensemble.get_name()) if self.musical_ensemble else "ERROR -- musical_ensemble_id is Null"

    def __repr__(self):
        return 'BioMusicalEnsemble(musical_ensemble_id="{}",name="{}",bio="{}")'.format(
            self.musical_ensemble.id, 
            self.musical_ensemble.get_name(),
            self.biografia[:40]
            )
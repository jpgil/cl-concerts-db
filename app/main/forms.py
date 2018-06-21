from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectMultipleField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError, DataRequired, Length, Optional
from flask_babel import _, lazy_gettext as _l
from app.models import User, Country, Instrument, InstrumentType, Person

class NonValidatingSelectField(SelectField):
    def pre_validate(self, form):
        pass

class NonValidatingSelectMultipleField(SelectMultipleField):
    def pre_validate(self, form):
        pass
    
class EditSimpleElementForm(FlaskForm):
    name=StringField(_l('Nombre'),validators=[DataRequired()])
    submit = SubmitField(_l('Guardar'))
    def __init__(self,dbmodel,original_name,*args, **kwargs):
        super(EditSimpleElementForm, self).__init__(*args, **kwargs)
        self.original_name = original_name     
        self.dbmodel = dbmodel
    def validate_name(self,name):
        if(name.data != self.original_name):
            db_elem_instance = self.dbmodel.query.filter_by(name=name.data).first()
            if db_elem_instance is not None:
                raise ValidationError(_('Este nombre ya está registrado, por favor, use uno diferente'))        


class EditInstrumentForm(FlaskForm):
    name=StringField(_l('Nombre'),validators=[DataRequired()])
    instrument_type= NonValidatingSelectMultipleField(label=_("Tipo de Instrumento"),choices=[],validators=[DataRequired()])
    submit = SubmitField(_l('Guardar'))
    def __init__(self, original_name ,*args, **kwargs):
        super(EditInstrumentForm, self).__init__(*args, **kwargs)
        self.original_name = original_name     
    def validate_name(self,name):
        if(name.data != self.original_name):
            db_elem_instance = Instrument.query.filter_by(name=name.data).first()
            if db_elem_instance is not None:
                raise ValidationError(_('Este nombre ya está registrado, por favor, use uno diferente'))        


class EditPersonForm(FlaskForm):
    first_name=StringField(_l('Nombre'))
    last_name=StringField(_l('Apellido'))    
    nationalities= NonValidatingSelectMultipleField(label=_("Nacionalidades"),choices=[])
    birth_date=DateField(_('Nacimiento'),validators=[Optional()])
    death_date=DateField(_('Muerte'),validators=[Optional()])
    biography=TextAreaField(_('Información Biográfica'))
    submit = SubmitField(_l('Guardar'))
    def __init__(self, original_person ,*args, **kwargs):
        super(EditPersonForm, self).__init__(*args, **kwargs)
        self.original_first_name=None
        self.original_last_name=None
        if original_person:
            self.original_first_name=original_person.first_name
            self.original_last_name=original_person.last_name
    def validate_name(self,name):
        if(self.first_name.data != self.original_first_name and self.last_name.data != self.original_last_name):
            db_elem_instance = Person.query.filter_by(first_name=self.first_name.data).filter_by(last_name=self.last_name.data).first()
            if db_elem_instance is not None:
                raise ValidationError(_('Este nombre ya está registrado, por favor, use uno diferente'))
        if (self.first_name.data == '') and (self.last_name.data == ''):
            raise ValidationError(_('Debe ingresar al menos un nombre o apellido'))            
    def validate_first_name(self,first_name):
        self.validate_name(first_name)
    def validate_last_name(self,last_name):
        self.validate_name(last_name)
    def validate_birth_date(self,birth):
        if self.birth_date.data and self.death_date.data:
            if (self.birth_date.data>self.death_date.data):
               raise ValidationError(_('La fecha de nacimiento no puede ser mayor a la de muerte')) 

#class NewSimpleElementForm(FlaskForm):
#    name=StringField(_l('Nombre'),validators=[DataRequired()])
#    submit = SubmitField(_l('Guardar'))
#    def validate_name(self,name):
#        db_elem_instance = self.dbmodel.query.filter_by(name=name.data).first()
#        if db_elem_instance is not None:
#                raise ValidationError(_('Este nombre ya está registrado, por favor, use uno diferente'))        
                
#
#class EditProfileForm(FlaskForm):
#    username = StringField(_l('Username'), validators=[DataRequired()])
#    about_me = TextAreaField(_l('About me'),
#                             validators=[Length(min=0, max=140)])
#    submit = SubmitField(_l('Submit'))
#
#    def __init__(self, original_username, *args, **kwargs):
#        super(EditProfileForm, self).__init__(*args, **kwargs)
#        self.original_username = original_username
#
#    def validate_username(self, username):
#        if username.data != self.original_username:
#            user = User.query.filter_by(username=self.username.data).first()
#            if user is not None:
#                raise ValidationError(_('Please use a different username.'))
#
#
#class PostForm(FlaskForm):
#    post = TextAreaField(_l('Say something'), validators=[DataRequired()])
#    submit = SubmitField(_l('Submit'))
#
#
#class SearchForm(FlaskForm):
#    q = StringField(_l('Search'), validators=[DataRequired()])
#
#    def __init__(self, *args, **kwargs):
#        if 'formdata' not in kwargs:
#            kwargs['formdata'] = request.args
#        if 'csrf_enabled' not in kwargs:
#            kwargs['csrf_enabled'] = False
#        super(SearchForm, self).__init__(*args, **kwargs)
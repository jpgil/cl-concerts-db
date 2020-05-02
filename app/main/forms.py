from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectMultipleField, SelectField, IntegerField, DateField
from wtforms.validators import ValidationError, DataRequired, Length, Optional, NumberRange, InputRequired
from flask_babel import _, lazy_gettext as _l
from app.models import  *

class NonValidatingSelectField(SelectField):
    def pre_validate(self, form):
        pass

class NonValidatingSelectMultipleField(SelectMultipleField):
    def pre_validate(self, form):
        pass
    
class EditSimpleElementForm(FlaskForm):
    name=StringField(_l('Nombre'))
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
    instrument_type= NonValidatingSelectMultipleField(label=_("Tipo de Instrumento"),choices=[],validators=[Optional()])
    submit = SubmitField(_l('Guardar'))
    def __init__(self, original_name ,*args, **kwargs):
        super(EditInstrumentForm, self).__init__(*args, **kwargs)
        self.original_name = original_name     
    def validate_name(self,name):
        if(name.data != self.original_name):
            db_elem_instance = Instrument.query.filter_by(name=name.data).first()
            if db_elem_instance is not None:
                raise ValidationError(_('Este nombre ya está registrado, por favor, use uno diferente'))        

class EditMusicalEnsembleForm(FlaskForm):
    name=StringField(_l('Nombre'),validators=[DataRequired()])
    musical_ensemble_type= NonValidatingSelectMultipleField(label=_("Tipo de Agrupación Musical"),choices=[],validators=[Optional()])
    person= NonValidatingSelectMultipleField(label=_("Persona"),choices=[],validators=[Optional()])
    activity= NonValidatingSelectMultipleField(label=_("Actividad"),choices=[],validators=[Optional()])

    additional_info=TextAreaField(_('Información Adicional'))
    submit = SubmitField(_l('Guardar'))
    def __init__(self, original_name ,*args, **kwargs):
        super(EditMusicalEnsembleForm, self).__init__(*args, **kwargs)
        self.original_name = original_name     
    def validate_name(self,name):
        if(name.data != self.original_name):
            db_elem_instance = MusicalEnsemble.query.filter_by(name=name.data).first()
            if db_elem_instance is not None:
                raise ValidationError(_('Este nombre ya está registrado, por favor, use uno diferente'))        
                
class EditMusicalPieceForm(FlaskForm):
    name=StringField(_l('Título'),validators=[DataRequired()])
    composers= NonValidatingSelectMultipleField(label=_("Compositor"),choices=[],validators=[DataRequired()])
    composition_year=IntegerField(_('Año de composición'),validators=[Optional(), NumberRange(min=1, max=3000, message=_('El año ingresado no es válido'))])
    instruments = NonValidatingSelectMultipleField(label=_("Instrumentos"),choices=[],validators=[Optional()])
    instrumental_lineup = StringField(_l('Formación Instrumental'))
    text = StringField(_l('Texto'))
    submit = SubmitField(_l('Guardar'))
    def __init__(self, original_name ,*args, **kwargs):
        super(EditMusicalPieceForm, self).__init__(*args, **kwargs)
        self.original_name = original_name     
   

class EditActivityForm(FlaskForm):
    name=StringField(_l('Nombre'),validators=[DataRequired()])
    instrument= NonValidatingSelectMultipleField(label=_("Instrumento"),choices=[],validators=[Optional()])
    submit = SubmitField(_l('Guardar'))
    def __init__(self, original_name ,*args, **kwargs):
        super(EditActivityForm, self).__init__(*args, **kwargs)
        self.original_name = original_name     
    def validate_name(self,name):
        if(name.data != self.original_name):
            db_elem_instance = Activity.query.filter_by(name=name.data).first()
            if db_elem_instance is not None:
                raise ValidationError(_('Este nombre ya está registrado, por favor, use uno diferente'))       
                

class EditPersonForm(FlaskForm):
    first_name=StringField(_l('Nombre'))
    last_name=StringField(_l('Apellido'))    
    nationalities= NonValidatingSelectMultipleField(label=_("Nacionalidades"),choices=[])
    birth_year=IntegerField(_('Año de Nacimiento'),validators=[Optional()])
    death_year=IntegerField(_('Año de Muerte'),validators=[Optional()])
    gender= NonValidatingSelectMultipleField(label=_("Sexo"),choices=[],validators=[DataRequired()])
    biography=TextAreaField(_('Información Biográfica'))
    submit = SubmitField(_l('Guardar'))
    def __init__(self, original_person ,*args, **kwargs):
        super(EditPersonForm, self).__init__(*args, **kwargs)
        self.original_first_name=None
        self.original_last_name=None
        self.original_gender=None
        if original_person:
            self.original_first_name=original_person.first_name
            self.original_last_name=original_person.last_name
            self.original_gender=original_person.gender.id
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
    def validate_birth_year(self,birth):
        if self.birth_year.data and self.death_year.data:
            if (int(self.birth_year.data)>int(self.death_year.data)):
               raise ValidationError(_('La fecha de nacimiento no puede ser mayor a la de muerte')) 


class EditLocationForm(FlaskForm):
    name=StringField(_l('Nombre'),validators=[DataRequired()])
    address=StringField(_l('Dirección'))
    city= NonValidatingSelectMultipleField(label=_("Ciudad"),choices=[],validators=[DataRequired()])
    additional_info=TextAreaField(_('Información Adicional'))
    submit = SubmitField(_l('Guardar'))
    def __init__(self, original_name ,*args, **kwargs):
        super(EditLocationForm, self).__init__(*args, **kwargs)
        self.original_name = original_name     
    def validate_name(self,name):
        if(name.data != self.original_name):
            db_elem_instance = Location.query.filter_by(name=name.data).first()
            if db_elem_instance is not None:
                raise ValidationError(_('Este nombre ya está registrado, por favor, use uno diferente'))        

class EditOrganizationForm(FlaskForm):
    name=StringField(_l('Nombre'),validators=[DataRequired()])
    additional_info=TextAreaField(_('Información Adicional'))
    submit = SubmitField(_l('Guardar'))
    def __init__(self, original_name ,*args, **kwargs):
        super(EditOrganizationForm, self).__init__(*args, **kwargs)
        self.original_name = original_name     
    def validate_name(self,name):
        if(name.data != self.original_name):
            db_elem_instance = Organization.query.filter_by(name=name.data).first()
            if db_elem_instance is not None:
                raise ValidationError(_('Este nombre ya está registrado, por favor, use uno diferente'))        
                
class EditEventForm(FlaskForm):
    name=StringField(_l('Nombre del Evento'),validators=[])
    organizations= NonValidatingSelectMultipleField(label=_("Organizadores"),choices=[],validators=[])
    location= NonValidatingSelectMultipleField(label=_("Lugar"),choices=[],validators=[DataRequired()])
    event_year = IntegerField(label='Año/Mes/Día',validators=[DataRequired(), NumberRange(min=1, max=3000, message=_('El año ingresado no es válido'))])
    event_month = IntegerField(validators=[Optional(),NumberRange(min=1, max=12,message=_("El mes debe corresponder a un número entre 1 y 12"))])
    event_day = IntegerField(validators=[Optional(),NumberRange(min=1, max=31,message=_("El díá debe corresponder a un número entre 1 y 31"))])
    information=TextAreaField(_('Información'))
    event_type= NonValidatingSelectMultipleField(label=_("Tipo de Evento"),choices=[],validators=[DataRequired()])
    cycle= NonValidatingSelectMultipleField(label=_("Ciclo/Festival"),choices=[],validators=[DataRequired()])
    # the following fields will no be read used when created a new event. They are placed here just for allowing to 
    # appear for adding new participants/actividades/performances/relations
    person= NonValidatingSelectMultipleField(label=_("Persona"),choices=[],validators=[Optional()])
    activity= NonValidatingSelectMultipleField(label=_("Actividad"),choices=[],validators=[Optional()])
    musical_ensemble= NonValidatingSelectMultipleField(label=_("Agrupación Musical"),choices=[],validators=[Optional()])
    musical_piece= NonValidatingSelectMultipleField(label=_("Obra"),choices=[],validators=[Optional()])
    premiere_type= NonValidatingSelectMultipleField(label=_("Estreno"),choices=[],validators=[Optional()])
    performance= NonValidatingSelectMultipleField(label=_("Interpretación"),choices=[],validators=[Optional()])
    participant= NonValidatingSelectMultipleField(label=_("Participante"),choices=[],validators=[Optional()])

    
    submit = SubmitField(_l('Guardar'))
    def __init__(self,original_event,*args, **kwargs):
        super(EditEventForm, self).__init__(*args, **kwargs)
        self.original_name=None
        if original_event:
            self.original_name=original_event.name


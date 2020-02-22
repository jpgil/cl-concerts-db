from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField
from wtforms_alchemy.fields import QuerySelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l
from app.models import User, Profile
from flask_admin.form.widgets import Select2Widget


class LoginForm(FlaskForm):
    email = StringField(_l('e-mail'), validators=[DataRequired()])
    password = PasswordField(_l('Contraseña'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Recuérdame'))
    submit = SubmitField(_l('Log in'))



def profile_query():
    return Profile.query

class RegistrationForm(FlaskForm):
    first_name = StringField(_l('Nombre'), validators=[DataRequired()])
    last_name = StringField(_l('Apellido'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Contraseña'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repetir Contraseña'), validators=[DataRequired(),
                                           EqualTo('password')])
    perfil = QuerySelectField(query_factory=profile_query, allow_blank=False, get_label = 'name', widget=Select2Widget()) 
    submit = SubmitField(_l('Registrase'))
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_('Por favor, use un e-mail diferente.'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Requerir reset de contraseña'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Contraseña'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repetir Contraseña'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Requerir reset de contraseña'))

class EditProfileForm(FlaskForm):
    first_name = StringField(_l('Nombre'), validators=[DataRequired()])
    last_name = StringField(_l('Apellido'), validators=[DataRequired()])
    email = StringField(_l('e-mail'),render_kw={'readonly': True})
    password = PasswordField(_l('Contraseña (dejar en blanco para mantener)'))
    password2 = PasswordField(
        _l('Repetir Contraseña'), validators=[ EqualTo('password')])
    submit = SubmitField(_l('Guardar Cambios'))

class EditUserForm(FlaskForm):
    profile_id = HiddenField('original_profile_id')
    first_name = StringField(_l('Nombre'), validators=[DataRequired()])
    last_name = StringField(_l('Apellido'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    perfil = QuerySelectField(query_factory=profile_query, allow_blank=False, get_label = 'name', widget=Select2Widget(), render_kw={'autocomplete': False}) 
    password = PasswordField(_l('Contraseña (dejar en blanco para mantener)'), render_kw={'autocomplete': False})
    password2 = PasswordField(
        _l('Repetir Contraseña'), validators=[ EqualTo('password')], render_kw={'autocomplete': False})
    submit = SubmitField(_l('Guardar Cambios'))
    def __init__(self, original_email ,*args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.original_email = original_email    
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError(_('E-mail ya registrado, por favor, use un e-mail diferente.'))

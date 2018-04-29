from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l
from app.models import User


class LoginForm(FlaskForm):
    email = StringField(_l('e-mail'), validators=[DataRequired()])
    password = PasswordField(_l('Contraseña'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Recuérdame'))
    submit = SubmitField(_l('Log in'))


class RegistrationForm(FlaskForm):
    first_name = StringField(_l('Nombre'), validators=[DataRequired()])
    last_name = StringField(_l('Apellido'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Contraseña'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repetir Contraseña'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Registrase'))



    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_('Por favor, use un email diferente.'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Requerir reseteo de contraseña'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Contraseña'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repetir Contraseña'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Requerir reseteo de contraseña'))

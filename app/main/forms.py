from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User, Country

class EditSimpleElementForm(FlaskForm):
    name=StringField(_l('Nombre'),validators=[DataRequired()])
    submit = SubmitField(_l('Guardar'))
    def __init__(self,dbmodel, original_name ,*args, **kwargs):
        super(EditSimpleElementForm, self).__init__(*args, **kwargs)
        self.original_name = original_name     
        self.dbmodel = dbmodel

    def validate_name(self,name):
        if(name.data != self.original_name):
            db_elem_instance = self.dbmodel.query.filter_by(name=name.data).first()
            if db_elem_instance is not None:
                raise ValidationError(_('Este nombre ya está registrado, por favor, use uno diferente'))        
        
class NewSimpleElementForm(FlaskForm):
    name=StringField(_l('Nombre'),validators=[DataRequired()])
    submit = SubmitField(_l('Guardar'))
    def validate_name(self,name):
        db_elem_instance = self.dbmodel.query.filter_by(name=name.data).first()
        if db_elem_instance is not None:
                raise ValidationError(_('Este nombre ya está registrado, por favor, use uno diferente'))        
                
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

from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User, Country

class EditSimpleElement(FlaskForm):
    def __init__(self,dbmodel,title, original_name,is_new ,*args, **kwargs):
        super(EditSimpleElement, self).__init__(*args, **kwargs)
        self.original_name = original_name
        self.title = title       
        self.is_new = is_new
        self.dbmodel = dbmodel
        self.name = StringField(self.title,validators=[DataRequired()])
        if original_name:
            self.name.data = original_name

    submit = SubmitField(_l('Guardar'))
    def validate_name(self):
        if(self.name.data != self.original_name or self.is_new):
            db_elem_instance = self.dbmodel.query.filter_by(name=self.name.data).first()
            if db_elem_instance is not None:
                raise ValidationError(_('Este %s ya fue ingresado, por favor, use un nombre diferente'%self.title))        
        
        
        
    
class EditCountryForm(FlaskForm):
    def __init__(self, original_country_name, is_new, *args, **kwargs):
        super(EditCountryForm, self).__init__(*args, **kwargs)
        self.original_country_name = original_country_name

#    country_name = StringField(_l('País'), validators=[DataRequired()])
#        if not self.is_new:
#            country_name.data = original_country_name  
#    submit = SubmitField(_l('Guardar'))
#    def validate_country_name(self, email):
#        if( country_name.data != original_country_name or self.is_new):
#            country = Country.query.filter_by(name=country_name.data).first()
#            if country is not None:
#                raise ValidationError(_('Este país ya fue ingresado, por favor, use un nombre diferente'))        


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

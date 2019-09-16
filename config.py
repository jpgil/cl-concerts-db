import os
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))
class Config(object):
    # will be used for generating hashes for codification. Use any prase here    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-real-secret-one'
    # The database URL. It should be compatible with SQL Alchemy. It defauls to sqlite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    # See https://flask-sqlalchemy.palletsprojects.com/en/2.x/signals/ . You'll probably keep it as is.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # the following parameters correspond to the mail server configuration. This is for sending emails with the errors
    # and backtraces to the admin (MAIL_RECEIVER). If you don't setup this, you can always directly look in the logs
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') in ['True' , 'true' ]
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') in ['True' , 'true' ]
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SENDER = os.environ.get('MAIL_SENDER')    
    MAIL_RECEIVER = os.environ.get('MAIL_RECEIVER')    
    # The number of items displayed by default in the pages (used for pagination)
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE') or 5)
    # where the uploaded files wil be stored. There an 'uploads' directory will be created
    UPLOADS_DEFAULT_DEST = basedir
    # language on which is expected to have translations.
    LANGUAGES = ['es', 'en']
    def __init__(self):
       print(os.path.join(basedir, '.env'))    
#       print("Using SQLALCHEMY_DATABASE_URI=%s",SQLALCHEMY_DATABASE_URI)


import os
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-real-secret-one'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') in ['True' , 'true' ]
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') in ['True' , 'true' ]
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SENDER = os.environ.get('MAIL_SENDER')    
    MAIL_RECEIVER = os.environ.get('MAIL_RECEIVER')    
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE') or 5)
    UPLOADS_DEFAULT_DEST = basedir
    LANGUAGES = ['es', 'en']
    def __init__(self):
       print(os.path.join(basedir, '.env'))    
#       print("Using SQLALCHEMY_DATABASE_URI=%s",SQLALCHEMY_DATABASE_URI)


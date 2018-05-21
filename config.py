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
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE') or 5)
    LANGUAGES = ['es', 'en']
    ADMINS = ['your-email@example.com']
    def __init__(self):
       print(os.path.join(basedir, '.env'))    
       print("Using SQLALCHEMY_DATABASE_URI=%s",SQLALCHEMY_DATABASE_URI)


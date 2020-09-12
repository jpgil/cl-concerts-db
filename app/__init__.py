import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from flask_uploads import UploadSet, configure_uploads, AllExcept
#from elasticsearch import Elasticsearch
from flask_caching import Cache
from config import Config
from apscheduler.schedulers.background import BackgroundScheduler
#from app.main import events_cache

db = SQLAlchemy()
migrate = Migrate(compare_type=True)
login = LoginManager()
login.login_view = 'users.login'
login.login_message = _l('Por favor, loguearse para ver esta página.')
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()
babel = Babel()
cache = Cache(config={'CACHE_TYPE': 'simple'})
scheduler = BackgroundScheduler()
files_collection = UploadSet('uploads', AllExcept(('exe', 'iso')))



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    cache.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)
    configure_uploads(app, files_collection)
#    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
#        if app.config['ELASTICSEARCH_URL'] else None

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.users import bp as users_bp
    app.register_blueprint(users_bp, url_prefix='/users')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr=app.config['MAIL_SENDER'],
                toaddrs=app.config['MAIL_RECEIVER'], subject='Error en cl-concerts-db',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/cl-concerts-db.log',
                                           maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.DEBUG)
        app.logger.info('cl-concerts-db startup')

    # WEB version added as blueprint
    from app.public import bp as public_bp
    app.register_blueprint(public_bp, url_prefix='/public')
    return app



@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


from app import models

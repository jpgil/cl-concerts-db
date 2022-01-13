from app import create_app, db, cli
from app.models import User, History, Profile

app = create_app()

import config
from flask import session
session['language'] = config.defaultlang # As soon as the app is created, we create a key for its language.
                                         # The default language is stored in config.py as defaultlang in root folder.

cli.register(app)



@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'History': History , 'Profile': Profile}


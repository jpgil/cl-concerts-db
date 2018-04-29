from app import create_app, db, cli
from app.models import User, History, Profile

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'History': History , 'Profile': Profile}


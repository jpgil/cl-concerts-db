from flask import Blueprint

bp = Blueprint('public', __name__)

from app.public import routes


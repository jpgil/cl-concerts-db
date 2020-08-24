from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import api_methods, web_methods, errors


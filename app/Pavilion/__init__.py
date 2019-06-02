from flask import Blueprint

Pavilion = Blueprint('Pavilion', __name__ , template_folder='templates')

from app.Pavilion import routes, events

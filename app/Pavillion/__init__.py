from flask import Blueprint

Pavillion = Blueprint('crowd_control', __name__ , template_folder='templates')

from app.Pavillion import routes, events

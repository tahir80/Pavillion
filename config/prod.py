import os
DEBUG = False
SECRET_KEY='YOUR_SECRET_KEY'
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_TRACK_MODIFICATIONS=False

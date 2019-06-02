#app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO

from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.qualification import Qualifications, PercentAssignmentsApprovedRequirement, NumberHitsApprovedRequirement
from boto.mturk.price import Price
import boto3
from flask_cors import CORS
db = SQLAlchemy()

bootstrap = Bootstrap()
login_manager = LoginManager()

socketio = SocketIO()



##########Amazon Mechanical Turk Settings################################
AWS_ACCESS_KEY_ID = "REPLACE_WITH_YOUR_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "REPLACE_WITH_YOUR_SECRET_ACCESS_KEY_ID"
DEV_ENVIROMENT_BOOLEAN = True
DEBUG = True

AMAZON_HOST = ''

if DEV_ENVIROMENT_BOOLEAN:
    AMAZON_HOST = "https://workersandbox.mturk.com/mturk/externalSubmit"
else:
    AMAZON_HOST = "https://www.mturk.com/mturk/externalSubmit"

#for boto3
region_name = 'us-east-1'
# Use this endpoint_url instead to use production
# endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'
endpoint_url = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'


connection = boto3.client('mturk',
        endpoint_url = endpoint_url,
        region_name = region_name,
        aws_access_key_id = AWS_ACCESS_KEY_ID,
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
        )


connection2 = MTurkConnection(aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                             host=AMAZON_HOST)
#####################END of AMT settings####################################


# we need to tell Flask about the login view
login_manager.login_view = 'authentication.do_the_login'
# we can set the level of security, in this case, we chose strong.
# the flask will delete the session or cookies and forces the user to login again
# to protect the data
login_manager.session_protection = 'strong'

bcrypt = Bcrypt()


def create_app(config_type):

    app = Flask(__name__)

    CORS(app)

    configuration = os.path.join(os.getcwd(), 'config', config_type + '.py')
    #  to load the configuration file
    app.config.from_pyfile(configuration)

    #  to attach the Flask app with DB instance created on line # 7
    db.init_app(app)

    #you also need to initialize Bootstrap with flask ( or integgrate flask app with bootstrap)
    bootstrap.init_app(app)

    login_manager.init_app(app)
    bcrypt.init_app(app)

    socketio.init_app(app)

    # import Blueprint variable (main) from catalog sub-package
    from app.admin_panel import main   # import blueprint (the name was main)
    app.register_blueprint(main) # register blueprint

    # import Blueprint variable (authentication) from auth sub-package
    from app.auth import authentication   # import blueprint (the name was main)
    app.register_blueprint(authentication) # register blueprint

    from app.Pavilion import Pavilion
    app.register_blueprint(Pavilion)

    return app

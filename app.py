import os

from flask import Flask

from models import db
from oauth import configure_oauth
from route import login_manager, bp

import logging
import sys


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', '049qwmc-scweccvw883h04')
    SESSION_COOKIE_NAME = 'session_auth_server' # Ensure unique session cookie name
    # TODO: Replace below with your database credentials
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URI',  #'mysql+mysqlconnector://root:Pawc10mk1???@localhost/oauth_server' #database-2.cgnk6i8mc853.us-east-1.rds.amazonaws.com
        'mysql+mysqlconnector://admin:Pawc10mk1???@54.226.39.79/oauth_server'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    configure_oauth(app)
    app.register_blueprint(bp)
    log = logging.getLogger('authlib')
    log.addHandler(logging.StreamHandler(sys.stdout))
    log.setLevel(logging.DEBUG)
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)

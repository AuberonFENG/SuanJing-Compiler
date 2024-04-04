from flask import Flask
from app.controller import user
import os

def register_blueprints(app):
    app.register_blueprint(user.userBP, url_prefix='/user')

def create_app():
    app = Flask(__name__)
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SECRET_KEY'] = os.urandom(24)
    register_blueprints(app)
    return app
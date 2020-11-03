import os
from flask import Flask

def create_app():
    app = Flask(__name__)

    # Load config.py
    app.config.from_pyfile('config.py')

    # Import blueprints
    from app.blueprints.api.routes import api
    from app.blueprints.main.routes import main

    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(api, url_prefix='/api')

    return app
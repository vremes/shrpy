from flask import Flask
from app.helpers.api import response
from werkzeug.exceptions import HTTPException
from app.helpers.delete_files import FileDeletionScheduler

file_deletion_scheduler = FileDeletionScheduler()

def create_app():
    app = Flask(__name__)

    # Load config.py
    app.config.from_pyfile('config.py')

    # Setup automatic file deletion
    file_deletion_scheduler.setup_scheduler()

    # jsonify HTTP errors
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        return response(e.code, e.name, description=e.description)

    # Import blueprints
    from app.blueprints.api.routes import api
    from app.blueprints.main.routes import main

    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(api, url_prefix='/api')

    return app
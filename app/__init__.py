from flask import Flask
from werkzeug.exceptions import HTTPException

from app.core.utils import (
    create_stdout_logger,
    http_error_handler,
    setup_db,
    get_config
)
from app.core.files import add_unsupported_mimetypes

db = setup_db()
logger = create_stdout_logger()
config = get_config()

def create_app() -> Flask:
    """Flask application factory."""
    app = Flask(__name__)

    # Add unsupported mimetypes to mimetypes module
    add_unsupported_mimetypes(config.mimetypes_custom_extensions)

    # jsonify HTTP errors
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        return http_error_handler(e)

    # Import blueprints
    from app.blueprints.main import main
    from app.blueprints.files import files
    from app.blueprints.urls import urls

    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(files, url_prefix='/api')
    app.register_blueprint(urls, url_prefix='/api')

    return app

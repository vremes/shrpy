# standard library imports
import logging

# pip imports
from flask import Flask
from werkzeug.exceptions import HTTPException

# local imports
from app.core.discord import CustomDiscordWebhook
from app.core.utils import (
    http_error_handler,
    add_unsupported_mimetypes,
    logger_handler,
    setup_db
)

db = setup_db()
discord_webhook = CustomDiscordWebhook()

def create_app():
    app = Flask(__name__)

    # Setup logging
    handler = logger_handler()
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    # Load config.py
    app.config.from_pyfile('config.py')

    # Set Discord webhook URLs
    discord_webhook.url = app.config.get('DISCORD_WEBHOOKS')

    # Set discord webhook timeout
    discord_webhook.timeout = app.config.get('DISCORD_WEBHOOK_TIMEOUT')

    # Add unsupported mimetypes to mimetypes module
    add_unsupported_mimetypes()

    # jsonify HTTP errors
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        return http_error_handler(e)

    # Import blueprints
    from app.blueprints.api import api
    from app.blueprints.main import main

    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(api, url_prefix='/api')

    return app
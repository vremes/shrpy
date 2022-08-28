# pip imports
from flask import Flask
from werkzeug.exceptions import HTTPException

# local imports
from app.config import Config
from app.core.discord import CustomDiscordWebhook
from app.core.utils import (
    create_stdout_logger,
    http_error_handler,
    add_unsupported_mimetypes,
    setup_db
)

db = setup_db()
logger = create_stdout_logger()
config = Config.from_env()
discord_webhook = CustomDiscordWebhook()

def create_app():
    app = Flask(__name__)

    # Set Discord webhook URLs
    discord_webhook.url = config.application.discord_webhooks

    # Set discord webhook timeout
    discord_webhook.timeout = config.application.discord_webhook_timeout

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
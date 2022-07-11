# pip imports
from flask import Flask
from werkzeug.exceptions import HTTPException

# local imports
from app.config import ApplicationConfig, UploaderConfig
from app.core.discord import CustomDiscordWebhook
from app.core.utils import (
    http_error_handler,
    add_unsupported_mimetypes,
    setup_db
)

db = setup_db()
discord_webhook = CustomDiscordWebhook()

# Configs
application_config = ApplicationConfig.from_environment_variables()
uploader_config = UploaderConfig.from_environment_variables()

def create_app():
    app = Flask(__name__)

    # Set Discord webhook URLs
    discord_webhook.url = application_config.discord_webhooks

    # Set discord webhook timeout
    discord_webhook.timeout = application_config.discord_webhook_timeout

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
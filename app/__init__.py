from flask import Flask
from app.helpers.utils import response
from werkzeug.exceptions import HTTPException
from app.helpers.delete_files import FileDeletionScheduler
from app.helpers.discord.webhooks import CustomDiscordWebhook

discord_webhook = CustomDiscordWebhook()
file_deletion_scheduler = FileDeletionScheduler()

def create_app():
    app = Flask(__name__)

    # Load config.py
    app.config.from_pyfile('config.py')

    # Set Discord webhook URLs
    discord_webhook.url = app.config.get('DISCORD_WEBHOOKS')

    # Set discord webhook timeout
    discord_webhook.timeout = app.config.get('DISCORD_WEBHOOK_TIMEOUT')

    # Setup automatic file deletion
    file_deletion_scheduler.setup()

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
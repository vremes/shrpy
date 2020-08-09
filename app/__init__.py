import os
from flask import Flask

def create_app():
    app = Flask(__name__)

    # Max upload file size
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # Path for uploaded files
    app.config['UPLOAD_DIR'] = os.path.join(app.root_path, 'uploads')

    # Allowed file extensions
    app.config['ALLOWED_EXTENSIONS'] = ['.png', '.jpg', '.jpeg', '.gif', '.webm', '.mp4']

    # Import blueprints
    from app.blueprints.api.routes import api
    from app.blueprints.main.routes import main

    # Register blueprints
    app.register_blueprint(main)
    app.register_blueprint(api, url_prefix='/api')

    return app
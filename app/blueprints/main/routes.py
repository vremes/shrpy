from flask import Blueprint, send_from_directory, current_app, request

main = Blueprint('main', __name__)

@main.route('/uploads/<filename>')
def uploads(filename):
    upload_dir = current_app.config['UPLOAD_DIR']

    return send_from_directory(upload_dir, filename)
from flask import Blueprint, send_from_directory, current_app, request

main = Blueprint('main', __name__)

@main.route('/uploads/<filename>')
def uploads(filename):
    upload_dir = current_app.config['UPLOAD_DIR']

    if request.args.get('dl') is True:
        return send_from_directory(upload_dir, filename, as_attachment=True)

    return send_from_directory(upload_dir, filename)
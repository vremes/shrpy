from app.helpers import auth
from app.helpers.api import response
from app.helpers.files import File
from flask import (
    Blueprint, request, abort, current_app, jsonify,
    url_for, render_template_string
)

api = Blueprint('api', __name__)

@api.route('/sharex')
def sharex():
    sharex_config = File.sharex_config()
    return jsonify(sharex_config)

@api.route('/upload', methods=['POST'])
@auth.auth_required
def upload():
    uploaded_file = request.files.get('file')

    if uploaded_file is None:
        return response(400, 'Invalid file')

    use_og_filename = request.headers.get('X-Use-Original-Filename', type=int) == 1

    # Our own class which utilises werkzeug.datastructures.FileStorage
    f = File(uploaded_file)
    f.use_original_filename = use_og_filename

    # Check if file is allowed
    if f.is_allowed() is False:
        return response(400, 'Invalid file type')

    # Get the filename
    filename = f.get_filename()

    # Save the file
    f.save()

    # Generate HMAC hash using Flask's secret key and filename
    hmac_hash = File.create_hmac_hash(filename, current_app.secret_key)

    # Return JSON
    return jsonify(
            {
                'filename': filename,
                'url': url_for('main.uploads', filename=filename, _external=True),
                'delete_url': url_for('api.delete_file', hmac_hash=hmac_hash, filename=filename, _external=True)
            }
        )

@api.route('/delete-file/<hmac_hash>/<filename>')
def delete_file(hmac_hash, filename):
    new_hmac_hash = File.create_hmac_hash(filename, current_app.secret_key)

    # If hash does not match
    if File.is_valid_hash(hmac_hash, new_hmac_hash) is False:
        return abort(404)

    if File.delete(filename) is False:
        return abort(404)

    message = render_template_string('{{ filename }} has been deleted, you can now close this page', filename=filename)
    return response(message=message)
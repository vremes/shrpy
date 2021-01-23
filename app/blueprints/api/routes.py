import os
from app.helpers import files, auth
from app.helpers.api import response
from flask import Blueprint, request, abort, current_app, jsonify, url_for, render_template_string

api = Blueprint('api', __name__)

@api.route('/sharex')
def sharex():
    sharex_config = files.sharex_config()
    return jsonify(sharex_config)

@api.route('/upload', methods=['POST'])
@auth.auth_required
def upload():
    uploaded_file = request.files.get('file')
    upload_directory = current_app.config['UPLOAD_DIR']
    use_og_filename = request.headers.get('X-Use-Original-Filename', type=int) == 1

    # If client did not send a file, abort
    if uploaded_file is None:
        return response(400, 'File upload failed, invalid file')

    # Check if file is allowed, based on file extension
    if files.is_allowed_file(uploaded_file.filename) is False:
        return response(400, 'Invalid file type')

     # Check if upload directory exists
    if os.path.isdir(upload_directory) is False:
        os.makedirs(upload_directory)

    modified_filename = files.get_modified_filename(uploaded_file.filename, use_og_filename)

    # Save file
    save_directory = os.path.join(upload_directory, modified_filename)
    uploaded_file.save(save_directory)

    # Generate HMAC hash using Flask's secret key and filename
    hmac_hash = files.create_hmac_hash(current_app.secret_key, modified_filename)

    return jsonify(
            {
                'filename': modified_filename, 
                'url': url_for('main.uploads', filename=modified_filename, _external=True),
                'delete_url': url_for('api.delete_file', hmac_hash=hmac_hash, filename=modified_filename, _external=True)
            }
        )

@api.route('/delete-file/<hmac_hash>/<filename>')
def delete_file(hmac_hash, filename):
    new_hmac_hash = files.create_hmac_hash(current_app.secret_key, filename)

    # If hash does not match
    if files.is_valid_hash(hmac_hash, new_hmac_hash) is False:
        return abort(404)

    file_path = os.path.join(current_app.config['UPLOAD_DIR'], filename)
    
    # If file does not exist
    if os.path.isfile(file_path) is False:
        return abort(404)

    os.remove(file_path)
    
    message = render_template_string('{{ filename }} has been deleted, you can now close this page', filename=filename)
    return response(message=message)
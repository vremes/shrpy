import os
import hmac
import hashlib
from uuid import uuid4
from werkzeug.utils import secure_filename
from flask import Blueprint, request, abort, current_app, jsonify, url_for, render_template_string

api = Blueprint('api', __name__)

@api.route('/sharex')
def sharex():
    response_dict = {
        "Version": "1.0.0",
        "DestinationType": "ImageUploader, FileUploader",
        "RequestMethod": "POST",
        "RequestURL": url_for('api.upload', _external=True),
        "Body": "MultipartFormData",
        "FileFormName": "file",
        "URL": "$json:url$",
        "DeletionURL": "$json:delete_url$"
    }

    if current_app.config.get('UPLOAD_PASSWORD') is not None:
        response_dict['Headers'] = {
            "Authorization": "YOUR-UPLOAD-PASSWORD-HERE"
        }

    return jsonify(response_dict)

@api.route('/upload', methods=['POST'])
def upload():
    upload_password = current_app.config.get('UPLOAD_PASSWORD')
    if upload_password is not None:
        authorization_header = request.headers.get('Authorization')

        if authorization_header != upload_password:
            return abort(401)

    uploaded_file = request.files.get('file')
    upload_directory = current_app.config['UPLOAD_DIR']
    allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']

    if uploaded_file is None:
        return abort(400)

    # Check if upload directory exists
    if os.path.isdir(upload_directory) is False:
        os.makedirs(upload_directory)

    original_filename = uploaded_file.filename.lower()
    
    # Extract filename and extension
    filename, ext = os.path.splitext(original_filename)

    if not ext in allowed_extensions:
        return abort(400, 'Invalid file extension!')

    # Filenames
    secure_original_filename = secure_filename(filename) # Secure version of the file's original filename
    new_filename = '{}-{}'.format(uuid4().hex, secure_original_filename) # Server generated filename + secure original filename
    full_filename = '{}{}'.format(new_filename, ext)
    save_directory = os.path.join(upload_directory, full_filename)

    # Save file
    uploaded_file.save(save_directory)

    # HMAC magic for deletion url
    secret_key = current_app.secret_key.encode('utf-8')
    hmac_data = full_filename.encode('utf-8')

    # Generate HMAC using Flask's secret key and filename
    signature = hmac.new(secret_key, hmac_data, hashlib.sha256).hexdigest()

    return jsonify(
            {
                'filename': full_filename, 
                'url': url_for('main.uploads', filename=full_filename, _external=True),
                'delete_url': url_for('api.delete_file', signature=signature, filename=full_filename, _external=True)
            }
        )

@api.route('/delete-file/<signature>/<filename>')
def delete_file(signature, filename):
    secret_key = current_app.secret_key.encode('utf-8')
    hmac_data = filename.encode('utf-8')

    hmac_signature = hmac.new(secret_key, hmac_data, hashlib.sha256).hexdigest()

    if hmac.compare_digest(hmac_signature, signature) is False:
        return abort(404)

    file_path = os.path.join(current_app.config['UPLOAD_DIR'], filename)
    
    if os.path.isfile(file_path) is False:
        return abort(404)

    os.remove(file_path)

    return render_template_string('{{ filename }} has been deleted, you can now close this page.', filename=filename)
import os
import hmac
import hashlib
from app.helpers import files, auth
from app.helpers.api import response
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
        "DeletionURL": "$json:delete_url$",
        "Headers": {
            "Authorization": "YOUR-UPLOAD-PASSWORD-HERE",
            "X-Use-Original-Filename": 1,
        },
        "ErrorMessage": "$json:status$"
    }

    return jsonify(response_dict)

@api.route('/upload', methods=['POST'])
@auth.auth_required
def upload():
    uploaded_file = request.files.get('file')
    upload_directory = current_app.config['UPLOAD_DIR']
    use_og_filename = request.headers.get('X-Use-Original-Filename', type=int) == 1

    if uploaded_file is None:
        return response(400, 'File upload failed, invalid file')

    # Check if upload directory exists
    if os.path.isdir(upload_directory) is False:
        os.makedirs(upload_directory)

    original_filename = uploaded_file.filename.lower()

    # Check if file is allowed
    if files.is_allowed_file(original_filename) is False:
        return response(400, 'Invalid file type')

    modified_filename = files.get_modified_filename(original_filename, use_og_filename)

    # Save file
    save_directory = os.path.join(upload_directory, modified_filename)
    uploaded_file.save(save_directory)

    # Generate HMAC using Flask's secret key and filename
    secret_key = current_app.secret_key.encode('utf-8')
    hmac_data = modified_filename.encode('utf-8')
    signature = hmac.new(secret_key, hmac_data,hashlib.sha256).hexdigest()

    return jsonify(
            {
                'filename': modified_filename, 
                'url': url_for('main.uploads', filename=modified_filename, _external=True),
                'delete_url': url_for('api.delete_file', signature=signature, filename=modified_filename, _external=True)
            }
        )

@api.route('/delete-file/<signature>/<filename>')
def delete_file(signature, filename):
    secret_key = current_app.secret_key.encode('utf-8')
    hmac_data = filename.encode('utf-8')
    hmac_signature = hmac.new(secret_key, hmac_data, hashlib.sha256).hexdigest()

    if hmac.compare_digest(hmac_signature, signature) is False:
        return abort(401)

    file_path = os.path.join(current_app.config['UPLOAD_DIR'], filename)
    
    if os.path.isfile(file_path) is False:
        return abort(404)

    os.remove(file_path)

    return render_template_string('{{ filename }} has been deleted, you can now close this page.', filename=filename)
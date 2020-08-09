import os
from uuid import uuid4
from flask import Blueprint, request, abort, current_app, jsonify, url_for

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
        "URL": "$json:url$"
    }

    return jsonify(response_dict)

@api.route('/upload', methods=['POST'])
def upload():
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
    new_filename = uuid4().hex
    full_filename = '{}{}'.format(new_filename, ext)
    save_directory = os.path.join(upload_directory, full_filename)

    # Save file
    uploaded_file.save(save_directory)

    return jsonify(
            {
                'filename': full_filename, 
                'url': url_for('main.uploads', filename=full_filename, _external=True)
            }
        )
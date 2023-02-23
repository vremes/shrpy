from http import HTTPStatus

from werkzeug.security import safe_join
from flask import Blueprint, jsonify, url_for, abort, request

from app import config, logger
from app.core.utils import (
    auth_required,
    create_hmac_hash,
    safe_str_comparison
)
from app.core.discord import (
    create_discord_webhooks,
    create_uploaded_file_embed,
    execute_webhooks_with_embed
)
from app.core.files import (
    get_file_extension_from_file,
    is_file_extension_allowed,
    create_directory,
    generate_filename,
    get_secure_filename,
    delete_file,
)

files = Blueprint('files', __name__)

@files.get('/sharex/upload')
def upload_config():
    return jsonify({
        "Name": "{} (File uploader)".format(request.host),
        "Version": "1.0.0",
        "DestinationType": "ImageUploader, FileUploader",
        "RequestMethod": "POST",
        "RequestURL": url_for('files.upload', _external=True),
        "Body": "MultipartFormData",
        "FileFormName": "file",
        "URL": "$json:url$",
        "DeletionURL": "$json:delete_url$",
        "Headers": {
            "Authorization": "YOUR-UPLOAD-PASSWORD-HERE",
        },
        "ErrorMessage": "$json:status$"
    })

@files.post('/upload')
@auth_required
def upload():
    f = request.files.get('file')

    if f is None:
        abort(HTTPStatus.BAD_REQUEST, 'Invalid file.')

    file_extension = get_file_extension_from_file(f.stream, config.magic_buffer_bytes)

    if is_file_extension_allowed(file_extension, config.allowed_extensions) is False:
        abort(HTTPStatus.UNPROCESSABLE_ENTITY, 'Invalid file type.')

    create_directory(config.upload_directory)

    filename = generate_filename()

    if config.use_original_filename:
        secure_filename = get_secure_filename(f.filename)
        filename = f'{filename}-{secure_filename}'

    save_filename = filename + file_extension
    save_path = safe_join(config.upload_directory, save_filename)

    f.save(save_path)

    hmac_hash = create_hmac_hash(save_filename, config.flask_secret)
    file_url = url_for('main.uploads', filename=save_filename, _external=True)
    deletion_url = url_for('files.delete_file_with_hash', hmac_hash=hmac_hash, filename=save_filename, _external=True)

    logger.info(f'Saved file: {save_filename}, URL: {file_url}, deletion URL: {deletion_url}')

    # Send data to Discord webhooks
    discord_webhooks = create_discord_webhooks(config.discord_webhook_urls, config.discord_webhook_timeout)
    if discord_webhooks:
        embed = create_uploaded_file_embed(file_url, deletion_url)
        execute_webhooks_with_embed(discord_webhooks, embed)

    # Return JSON
    return jsonify(url=file_url, delete_url=deletion_url)

@files.get('/delete-file/<hmac_hash>/<filename>')
def delete_file_with_hash(hmac_hash, filename):
    new_hmac_hash = create_hmac_hash(filename, config.flask_secret)

    # If digest is invalid
    if safe_str_comparison(hmac_hash, new_hmac_hash) is False:
        abort(HTTPStatus.NOT_FOUND)

    file_path = safe_join(config.upload_directory, filename)
    file_deleted = delete_file(file_path)

    if file_deleted is False:
        abort(HTTPStatus.GONE)

    logger.info(f'Deleted a file {filename}')

    return jsonify(message='This file has been deleted, you can now close this page.')

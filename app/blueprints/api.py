from http import HTTPStatus

from flask import Blueprint, jsonify, url_for, abort, request
from werkzeug.security import safe_join

from app import config, logger, discord_webhook
from app.core.main import UploadedFile, ShortUrl
from app.core.discord import create_short_url_embed, create_uploaded_file_embed
from app.core.utils import auth_required, create_directory, safe_str_comparison, create_hmac_hash

api = Blueprint('api', __name__)

@api.get('/sharex/upload')
def upload_config():
    return jsonify({
        "Name": "{} (File uploader)".format(request.host),
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
        },
        "ErrorMessage": "$json:status$"
    })

@api.get('/sharex/shorten')
def shorten_config():
    return jsonify({
        "Name": "{} (URL shortener)".format(request.host),
        "Version": "1.0.0",
        "DestinationType": "URLShortener",
        "RequestMethod": "POST",
        "Body": "MultipartFormData",
        "RequestURL": url_for('api.shorten', _external=True),
        "Headers": {
                "Authorization": "YOUR-UPLOAD-PASSWORD-HERE"
        },
        "Arguments": {
            "url": "$input$"
        },
        "URL": "$json:url$",
        "ErrorMessage": "$json:status$"
    })

@api.post('/upload')
@auth_required
def upload():
    f = request.files.get('file')

    if f is None:
        abort(HTTPStatus.BAD_REQUEST, 'Invalid file.')

    # Uploaded file
    uploaded_file = UploadedFile.from_file_storage_instance(f, config.upload)

    # Check if file is allowed
    if uploaded_file.is_allowed(config.upload.allowed_extensions) is False:
        abort(HTTPStatus.UNPROCESSABLE_ENTITY, 'Invalid file type.')

    # Ensure upload directory exists
    upload_directory = config.upload.directory
    create_directory(upload_directory)

    # Save the file
    save_path = safe_join(upload_directory, uploaded_file.full_filename)
    f.save(save_path)

    hmac_hash = uploaded_file.generate_filename_hmac(config.application.secret_key)

    file_url = url_for('main.uploads', filename=uploaded_file.full_filename, _external=True)
    deletion_url = url_for('api.delete_file', hmac_hash=hmac_hash, filename=uploaded_file.full_filename, _external=True)

    logger.info(f'Saved file: {uploaded_file.full_filename}, URL: {file_url}, deletion URL: {deletion_url}')

    # Send data to Discord webhook
    if discord_webhook.is_enabled:
        embed = create_uploaded_file_embed(file_url, deletion_url)
        discord_webhook.send_embed(embed)

    # Return JSON
    return jsonify(url=file_url, delete_url=deletion_url)

@api.post('/shorten')
@auth_required
def shorten():
    url = request.form.get('url')

    if url is None:
        abort(HTTPStatus.BAD_REQUEST, 'Invalid URL, missing url parameter in request body.')

    short_url = ShortUrl.from_url(url, config.upload)

    if short_url.is_valid() is False:
        abort(HTTPStatus.UNPROCESSABLE_ENTITY, 'Invalid URL.')

    # Add URL to database
    short_url.save_to_database()

    hmac_hash = short_url.generate_token_hmac(config.application.secret_key)

    shortened_url = url_for('main.short_url', token=short_url.token, _external=True)
    deletion_url = url_for('api.delete_short_url', hmac_hash=hmac_hash, token=short_url.token, _external=True)

    logger.info(f'Saved short URL: {shortened_url} for {short_url.url}, deletion URL: {deletion_url}')

    # Send data to Discord webhook
    if discord_webhook.is_enabled:
        embed = create_short_url_embed(short_url.url, shortened_url, deletion_url)
        discord_webhook.send_embed(embed)

    return jsonify(url=shortened_url)

@api.get('/delete-short-url/<hmac_hash>/<token>')
def delete_short_url(hmac_hash, token):
    new_hmac_hash = create_hmac_hash(token, config.application.secret_key)

    # If digest is invalid
    if safe_str_comparison(hmac_hash, new_hmac_hash) is False:
        abort(HTTPStatus.NOT_FOUND)

    if ShortUrl.delete_by_token(token) is False:
        abort(HTTPStatus.GONE)

    return jsonify(message='This short URL has been deleted, you can now close this page.')

@api.get('/delete-file/<hmac_hash>/<filename>')
def delete_file(hmac_hash, filename):
    new_hmac_hash = create_hmac_hash(filename, config.application.secret_key)

    # If digest is invalid
    if safe_str_comparison(hmac_hash, new_hmac_hash) is False:
        abort(HTTPStatus.NOT_FOUND)

    file_path = safe_join(config.upload.directory, filename)

    if UploadedFile.delete(file_path) is False:
        abort(HTTPStatus.GONE)

    logger.info(f'Deleted a file {filename}')

    return jsonify(message='This file has been deleted, you can now close this page.')

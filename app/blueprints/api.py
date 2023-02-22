from http import HTTPStatus
from secrets import token_urlsafe

from flask import Blueprint, jsonify, url_for, abort, request
from werkzeug.security import safe_join

from app import config, logger
from app.core.utils import (
    auth_required, safe_str_comparison,
    create_hmac_hash
)
from app.core.discord import (
    create_short_url_embed, create_uploaded_file_embed,
    create_discord_webhooks, execute_webhooks_with_embed
)
from app.core.files import (
    get_file_extension_from_file, is_file_extension_allowed, 
    create_directory, get_secure_filename,
    delete_file
)
from app.core.urls import (
    is_valid_url, add_https_scheme_to_url,
    save_url_and_token_to_database, delete_url_from_database_by_token
)

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

    file_extension = get_file_extension_from_file(f.stream, config.magic_buffer_bytes)

    if is_file_extension_allowed(file_extension, config.allowed_extensions) is False:
        abort(HTTPStatus.UNPROCESSABLE_ENTITY, 'Invalid file type.')

    create_directory(config.upload.directory)

    filename = get_secure_filename(f.filename)
    save_filename = filename + file_extension
    save_path = safe_join(config.upload.directory, save_filename)

    f.save(save_path)

    hmac_hash = create_hmac_hash(save_filename, config.flask_secret)
    file_url = url_for('main.uploads', filename=save_filename, _external=True)
    deletion_url = url_for('api.delete_file', hmac_hash=hmac_hash, filename=save_filename, _external=True)

    logger.info(f'Saved file: {save_filename}, URL: {file_url}, deletion URL: {deletion_url}')

    # Send data to Discord webhooks
    discord_webhooks = create_discord_webhooks(config.discord_webhook_urls, config.discord_webhook_timeout)
    if discord_webhooks:
        embed = create_uploaded_file_embed(file_url, deletion_url)
        execute_webhooks_with_embed(discord_webhooks, embed)

    # Return JSON
    return jsonify(url=file_url, delete_url=deletion_url)

@api.post('/shorten')
@auth_required
def shorten():
    url = request.form.get('url')

    if is_valid_url(url) is False:
        abort(HTTPStatus.BAD_REQUEST, 'Invalid URL.')

    url = add_https_scheme_to_url(url)
    token = token_urlsafe(config.url_token_bytes)

    saved_to_database = save_url_and_token_to_database(url, token)

    if saved_to_database is False:
        abort(HTTPStatus.INTERNAL_SERVER_ERROR, 'Unable to save URL to database.')

    hmac_hash = create_hmac_hash(token, config.flask_secret)
    shortened_url = url_for('main.short_url', token=token, _external=True)
    deletion_url = url_for('api.delete_short_url', hmac_hash=hmac_hash, token=token, _external=True)

    logger.info(f'Saved short URL: {shortened_url} for {url}, deletion URL: {deletion_url}')

    # Send data to Discord webhooks
    discord_webhooks = create_discord_webhooks(config.discord_webhook_urls, config.discord_webhook_timeout)
    if discord_webhooks:
        embed = create_short_url_embed(url, shortened_url, deletion_url)
        execute_webhooks_with_embed(discord_webhooks, embed)

    return jsonify(url=shortened_url)

@api.get('/delete-short-url/<hmac_hash>/<token>')
def delete_short_url(hmac_hash, token):
    new_hmac_hash = create_hmac_hash(token, config.flask_secret)

    # If digest is invalid
    if safe_str_comparison(hmac_hash, new_hmac_hash) is False:
        abort(HTTPStatus.NOT_FOUND)

    if delete_url_from_database_by_token(token) is False:
        abort(HTTPStatus.GONE)

    return jsonify(message='This short URL has been deleted, you can now close this page.')

@api.get('/delete-file/<hmac_hash>/<filename>')
def delete_file(hmac_hash, filename):
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

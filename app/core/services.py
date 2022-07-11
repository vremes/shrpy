# standard library imports
from pathlib import Path
from http import HTTPStatus
from hmac import compare_digest

# pip imports
from flask import (
    Response, request, jsonify, 
    abort, url_for, send_from_directory,
    redirect
)
from werkzeug.security import safe_join

# local imports
from app.core.utils import create_hmac_hash
from app.core.main import ShortUrl, UploadedFile
from app.core.discord import create_short_url_embed, create_uploaded_file_embed
from app import discord_webhook, uploader_config, application_config

class FileService:
    @staticmethod
    def create() -> Response:
        f = request.files.get('file')

        if f is None:
            abort(HTTPStatus.BAD_REQUEST, 'Invalid file.')

        # Uploaded file
        uploaded_file = UploadedFile.from_file_storage_instance(f, uploader_config)

        # Check if file is allowed
        if uploaded_file.is_allowed() is False:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, 'Invalid file type.')

        # Save the file
        path = Path(uploader_config.upload_directory)
        path.mkdir(exist_ok=True)

        save_path = safe_join(path, uploaded_file.full_filename)
        f.save(save_path)

        hmac_hash = uploaded_file.generate_filename_hmac(application_config.secret_key)

        file_url = url_for('main.uploads', filename=uploaded_file.full_filename, _external=True)
        deletion_url = url_for('api.delete_file', hmac_hash=hmac_hash, filename=uploaded_file.full_filename, _external=True)

        application_config.logger.info(f'Saved file: {uploaded_file.full_filename}, URL: {file_url}, deletion URL: {deletion_url}')

        # Send data to Discord webhook
        if discord_webhook.is_enabled:
            embed = create_uploaded_file_embed(file_url, deletion_url)
            discord_webhook.send_embed(embed)

        # Return JSON
        return jsonify(url=file_url, delete_url=deletion_url)

    @staticmethod
    def delete() -> Response:
        filename = request.view_args.get('filename')
        hmac_hash = request.view_args.get('hmac_hash')
        new_hmac_hash = create_hmac_hash(filename, application_config.secret_key)

        # If digest is invalid
        if compare_digest(hmac_hash, new_hmac_hash) is False:
            abort(HTTPStatus.NOT_FOUND)

        file_path = safe_join(uploader_config.upload_directory, filename)

        if UploadedFile.delete(file_path) is False:
            abort(HTTPStatus.GONE)

        application_config.logger.info(f'Deleted a file {filename}')

        return jsonify(message='This file has been deleted, you can now close this page.')
    
    @staticmethod
    def config() -> Response:
        cfg = {
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
        }
        return jsonify(cfg)

    @staticmethod
    def get_by_filename() -> Response:
        filename = request.view_args.get('filename')
        return send_from_directory(uploaded_file_config.upload_directory, filename)

class ShortUrlService:
    @staticmethod
    def create() -> Response:
        url = request.form.get('url')

        if url is None:
            abort(HTTPStatus.BAD_REQUEST, 'Invalid URL, missing url parameter in request body.')

        short_url = ShortUrl.from_url(url, uploader_config)

        if short_url.is_valid() is False:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, 'Invalid URL.')

        # Add URL to database
        short_url.save_to_database()

        hmac_hash = short_url.generate_token_hmac(application_config.secret_key)

        shortened_url = url_for('main.short_url', token=short_url.token, _external=True)
        deletion_url = url_for('api.delete_short_url', hmac_hash=hmac_hash, token=short_url.token, _external=True)

        application_config.logger.info(f'Saved short URL: {shortened_url} for {short_url.url}, deletion URL: {deletion_url}')

        # Send data to Discord webhook
        if discord_webhook.is_enabled:
            embed = create_short_url_embed(short_url.url, shortened_url, deletion_url)
            discord_webhook.send_embed(embed)

        return jsonify(url=shortened_url)

    @staticmethod
    def delete() -> Response:
        token = request.view_args.get('token')
        hmac_hash = request.view_args.get('hmac_hash')
        new_hmac_hash = create_hmac_hash(token, application_config.secret_key)

        # If digest is invalid
        if compare_digest(hmac_hash, new_hmac_hash) is False:
            abort(HTTPStatus.NOT_FOUND)

        if ShortUrl.delete_by_token(token) is False:
            abort(HTTPStatus.GONE)

        return jsonify(message='This short URL has been deleted, you can now close this page.')

    @staticmethod
    def config() -> Response:
        cfg = {
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
        }
        return jsonify(cfg)

    @staticmethod
    def get_by_token() -> Response:
        token = request.view_args.get('token')
        short_url = ShortUrl.get_by_token(token)

        if short_url is None:
            abort(HTTPStatus.NOT_FOUND)

        return redirect(short_url)

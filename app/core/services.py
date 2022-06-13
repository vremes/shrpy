# standard library imports
from pathlib import Path
from http import HTTPStatus
from hmac import compare_digest

# pip imports
from flask import (
    Response, request, jsonify, 
    current_app, abort, url_for, 
    send_from_directory, redirect
)
from werkzeug.security import safe_join

# local imports
from app import discord_webhook
from app.core.main import ShortUrl, UploadedFile
from app.core.discord import ShortUrlEmbed, FileEmbed
from app.core.utils import create_hmac_hash

class FileService:
    @staticmethod
    def create() -> Response:
        f = request.files.get('file')

        if f is None:
            abort(HTTPStatus.BAD_REQUEST, 'Invalid file.')

        use_original_filename = request.headers.get('X-Use-Original-Filename', type=int) == 1

        # Uploaded file
        uploaded_file = UploadedFile.from_file_storage_instance(f, use_original_filename)

        # Check if file is allowed
        if uploaded_file.is_allowed() is False:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, 'Invalid file type.')

        # Save the file
        path = Path(current_app.config['UPLOAD_DIR'])
        path.mkdir(exist_ok=True)

        save_path = safe_join(path, uploaded_file.full_filename)
        f.save(save_path)

        hmac_hash = uploaded_file.generate_filename_hmac(current_app.secret_key)
        file_url = url_for('main.uploads', filename=uploaded_file.full_filename, _external=True)
        deletion_url = url_for('api.delete_file', hmac_hash=hmac_hash, filename=uploaded_file.full_filename, _external=True)

        current_app.logger.info(f'Saved file: {uploaded_file.full_filename}, URL: {file_url}, deletion URL: {deletion_url}')

        # Send data to Discord webhook
        if discord_webhook.is_enabled:
            discord_webhook.add_embed(
                EmbedService.get_file_embed(file_url, deletion_url)
            )
            discord_webhook.execute()

        # Return JSON
        return jsonify(url=file_url, delete_url=deletion_url)

    @staticmethod
    def delete() -> Response:
        filename = request.view_args.get('filename')
        hmac_hash = request.view_args.get('hmac_hash')
        new_hmac_hash = create_hmac_hash(filename, current_app.secret_key)

        # If digest is invalid
        if compare_digest(hmac_hash, new_hmac_hash) is False:
            abort(HTTPStatus.NOT_FOUND)

        if UploadedFile.delete(filename) is False:
            abort(HTTPStatus.GONE)

        current_app.logger.info(f'Deleted a file {filename}')

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
                "X-Use-Original-Filename": 1,
            },
            "ErrorMessage": "$json:status$"
        }
        return jsonify(cfg)

    @staticmethod
    def get_by_filename() -> Response:
        filename = request.view_args.get('filename')
        upload_dir = current_app.config['UPLOAD_DIR']
        return send_from_directory(upload_dir, filename)

class ShortUrlService:
    @staticmethod
    def create() -> Response:
        url = request.form.get('url')

        if url is None:
            abort(HTTPStatus.BAD_REQUEST, 'Invalid URL, missing url parameter in request body.')

        short_url = ShortUrl.from_url(url)

        if short_url.is_valid() is False:
            abort(HTTPStatus.UNPROCESSABLE_ENTITY, 'Invalid URL.')

        # Add URL to database
        short_url.save_to_database()

        hmac_hash = short_url.generate_token_hmac(current_app.secret_key)

        shortened_url = url_for('main.short_url', token=short_url.token, _external=True)
        deletion_url = url_for('api.delete_short_url', hmac_hash=hmac_hash, token=short_url.token, _external=True)

        current_app.logger.info(f'Saved short URL: {shortened_url} for {short_url.url}, deletion URL: {deletion_url}')

        # Send data to Discord webhook
        if discord_webhook.is_enabled:
            discord_webhook.add_embed(
                EmbedService.get_shorturl_embed(short_url.url, shortened_url, deletion_url)
            )
            discord_webhook.execute()

        return jsonify(url=shortened_url)

    @staticmethod
    def delete() -> Response:
        token = request.view_args.get('token')
        hmac_hash = request.view_args.get('hmac_hash')
        new_hmac_hash = create_hmac_hash(token, current_app.secret_key)

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

class EmbedService:
    @staticmethod
    def get_file_embed(url: str, deletion_url: str) -> FileEmbed:
        """Returns FileEmbed instance."""
        return FileEmbed(
            content_url=url, 
            deletion_url=deletion_url
        )

    @staticmethod
    def get_shorturl_embed(url: str, short_urL: str, deletion_url: str) -> ShortUrlEmbed:
        """Returns ShorturlEmbed instance."""
        return ShortUrlEmbed(
            original_url=url,
            content_url=short_urL,
            shortened_url=short_urL,
            deletion_url=deletion_url
        )

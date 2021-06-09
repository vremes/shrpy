# standard library imports
from http import HTTPStatus

# pip imports
from flask import (
    Response, request, jsonify, 
    current_app, abort, url_for, 
    send_from_directory, redirect
)

# local imports
from app import discord_webhook
from app.helpers.main import File, ShortUrl
from app.helpers.utils import Message, response, create_hmac_hexdigest, is_valid_digest

class FileService:
    @staticmethod
    def create() -> Response:
        uploaded_file = request.files.get('file')
        
        if uploaded_file is None:
            return response(HTTPStatus.BAD_REQUEST, Message.INVALID_FILE)

        # Our own class which utilises werkzeug.datastructures.FileStorage
        use_og_filename = bool(request.headers.get('X-Use-Original-Filename', type=int))
        f = File(uploaded_file, use_og_filename)

        # Check if file is allowed
        if f.is_allowed() is False:
            return response(HTTPStatus.UNPROCESSABLE_ENTITY, Message.INVALID_FILE_TYPE)

        # Save the file
        f.save()

        # Send data to Discord webhook
        if discord_webhook.is_enabled:
            discord_webhook.add_embed(
                f.embed()
            )
            discord_webhook.execute()

        # Return JSON
        return jsonify(url=f.url, delete_url=f.deletion_url)

    @staticmethod
    def delete() -> Response:
        filename = request.view_args.get('filename')
        hmac_hash = request.view_args.get('hmac_hash')
        new_hmac_hash = create_hmac_hexdigest(filename, current_app.secret_key)

        # If digest is invalid
        if is_valid_digest(hmac_hash, new_hmac_hash) is False:
            abort(HTTPStatus.NOT_FOUND)

        if File.delete(filename) is False:
            abort(HTTPStatus.GONE)

        return response(message=Message.FILE_DELETED)
    
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
            return response(HTTPStatus.BAD_REQUEST, Message.INVALID_URL)

        short_url = ShortUrl(url)

        if short_url.is_valid() is False:
            return response(HTTPStatus.UNPROCESSABLE_ENTITY, Message.INVALID_URL)

        # Add URL to database
        short_url.add()

        # Send data to Discord webhook
        if discord_webhook.is_enabled:
            discord_webhook.add_embed(
                short_url.embed()
            )
            discord_webhook.execute()

        return jsonify(url=short_url.shortened_url, delete_url=short_url.deletion_url)

    @staticmethod
    def delete() -> Response:
        token = request.view_args.get('token')
        hmac_hash = request.view_args.get('hmac_hash')
        new_hmac_hash = create_hmac_hexdigest(token, current_app.secret_key)

        # If digest is invalid
        if is_valid_digest(hmac_hash, new_hmac_hash) is False:
            abort(HTTPStatus.NOT_FOUND)

        if ShortUrl.delete(token) is False:
            abort(HTTPStatus.GONE)

        return response(message=Message.URL_DELETED)

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
            "DeletionURL": "$json:delete_url$",
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
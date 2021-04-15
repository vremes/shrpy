import flask
from http import HTTPStatus
from app import discord_webhook
from app.helpers import utils
from app.helpers.files import File
from app.helpers.urls import ShortUrl
from app.helpers.webhooks import EmbedType

class FileService:
    @staticmethod
    def create() -> flask.Response:
        uploaded_file = flask.request.files.get('file')
        
        if uploaded_file is None:
            return utils.response(HTTPStatus.BAD_REQUEST, 'Invalid file')

        # Our own class which utilises werkzeug.datastructures.FileStorage
        f = File(uploaded_file)

        # Check if file is allowed
        if f.is_allowed() is False:
            return utils.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'Invalid file type')

        # Set File.use_original_filename to True/False
        f.use_original_filename = bool(flask.request.headers.get('X-Use-Original-Filename', type=int))

        # Get the filename
        filename = f.get_filename()

        # Save the file
        f.save()

        # Generate HMAC hash using Flask's secret key and filename
        hmac_hash = utils.create_hmac_hash(filename, flask.current_app.secret_key)

        # Create URLs
        file_url = flask.url_for('main.uploads', filename=filename, _external=True)
        delete_url = flask.url_for('api.delete_file', hmac_hash=hmac_hash, filename=filename, _external=True)

        # Send data to Discord webhook
        if discord_webhook.is_enabled:
            discord_webhook.embed(file_url, delete_url, EmbedType.FILE)
            discord_webhook.send()

        # Return JSON
        return flask.jsonify(url=file_url, delete_url=delete_url)

    @staticmethod
    def delete() -> flask.Response:
        filename = flask.request.view_args.get('filename')
        hmac_hash = flask.request.view_args.get('hmac_hash')
        new_hmac_hash = utils.create_hmac_hash(filename, flask.current_app.secret_key)

        # If hash does not match
        if utils.is_valid_hash(hmac_hash, new_hmac_hash) is False:
            return flask.abort(HTTPStatus.NOT_FOUND)

        if File.delete(filename) is False:
            return flask.abort(HTTPStatus.GONE)

        message = flask.render_template_string('{{ filename }} has been deleted, you can now close this page', filename=filename)
        return utils.response(message=message)
    
    @staticmethod
    def config() -> flask.Response:
        cfg = {
            "Name": "{} (File uploader)".format(flask.request.host),
            "Version": "1.0.0",
            "DestinationType": "ImageUploader, FileUploader",
            "RequestMethod": "POST",
            "RequestURL": flask.url_for('api.upload', _external=True),
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
        return flask.jsonify(cfg)

    @staticmethod
    def get_by_filename(filename: str) -> flask.Response:
        upload_dir = flask.current_app.config['UPLOAD_DIR']
        return flask.send_from_directory(upload_dir, filename)

class ShortUrlService:
    @staticmethod
    def create() -> flask.Response:
        url = flask.request.form.get('url')

        if url is None:
            return utils.response(HTTPStatus.BAD_REQUEST, 'Invalid URL')

        short_url = ShortUrl(url)

        if short_url.is_valid() is False:
            return utils.response(HTTPStatus.UNPROCESSABLE_ENTITY, 'Invalid URL')

        # Add URL to database
        short_url.add()

        # Create HMAC for URL using token
        token = short_url.get_token()
        hmac_hash = utils.create_hmac_hash(token, flask.current_app.secret_key)

        # Create URLs
        short_url = flask.url_for('main.short_url', token=token, _external=True)
        delete_url = flask.url_for('api.delete_url', hmac_hash=hmac_hash, token=token, _external=True)

        # Send data to Discord webhook
        if discord_webhook.is_enabled:
            discord_webhook.embed(short_url, delete_url, EmbedType.SHORT_URL, original_url=url, shortened_url=short_url)
            discord_webhook.send()

        return flask.jsonify(url=short_url, delete_url=delete_url)

    @staticmethod
    def delete() -> flask.Response:
        token = flask.request.view_args.get('token')
        hmac_hash = flask.request.view_args.get('hmac_hash')
        new_hmac_hash = utils.create_hmac_hash(token, flask.current_app.secret_key)

        # If hash does not match
        if utils.is_valid_hash(hmac_hash, new_hmac_hash) is False:
            return flask.abort(HTTPStatus.NOT_FOUND)

        if ShortUrl.delete(token) is False:
            return flask.abort(HTTPStatus.GONE)

        return utils.response(message='This short URL has been deleted, you can now close this page')

    @staticmethod
    def config() -> flask.Response:
        cfg = {
            "Name": "{} (URL shortener)".format(flask.request.host),
            "Version": "1.0.0",
            "DestinationType": "URLShortener",
            "RequestMethod": "POST",
            "Body": "MultipartFormData",
            "RequestURL": flask.url_for('api.shorten', _external=True),
            "Headers": {
                "Authorization": "YOUR-UPLOAD-PASSWORD-HERE"
            },
            "Arguments": {
                "url": "$input$"
            },
            "URL": "$json:url$",
            "DeletionURL": "$json:delete_url$"
        }
        return flask.jsonify(cfg)

    @staticmethod
    def get_by_token(token: str) -> flask.Response:
        short_url = ShortUrl.get_by_token(token)

        if short_url is None:
            return flask.abort(HTTPStatus.NOT_FOUND)

        return flask.redirect(short_url)
from app.helpers import utils
from app import discord_webhook
from app.helpers.files import File
from app.helpers.urls import ShortUrl
from flask import (
    Blueprint, request, abort, current_app, jsonify,
    url_for, render_template_string
)

api = Blueprint('api', __name__)

@api.route('/sharex/upload')
def upload_config():
    config = File.sharex_config()
    return jsonify(config)

@api.route('/sharex/shorten')
def shorten_config():
    config = ShortUrl.sharex_config()
    return jsonify(config)

@api.route('/upload', methods=['POST'])
@utils.auth_required
def upload():
    uploaded_file = request.files.get('file')

    if uploaded_file is None:
        return utils.response(400, 'Invalid file')

    use_og_filename = request.headers.get('X-Use-Original-Filename', type=int) == 1

    # Our own class which utilises werkzeug.datastructures.FileStorage
    f = File(uploaded_file)
    f.use_original_filename = use_og_filename

    # Check if file is allowed
    if f.is_allowed() is False:
        return utils.response(400, 'Invalid file type')

    # Get the filename
    filename = f.get_filename()

    # Save the file
    f.save()

    # Generate HMAC hash using Flask's secret key and filename
    hmac_hash = utils.create_hmac_hash(filename, current_app.secret_key)

    # Create URLs
    file_url = url_for('main.uploads', filename=filename, _external=True)
    delete_url = url_for('api.delete_file', hmac_hash=hmac_hash, filename=filename, _external=True)

    # Send data to Discord webhook
    if discord_webhook.is_enabled:
        discord_webhook.embed(
            title='New file has been uploaded!',
            description=file_url,
            url=file_url,
            deletion_url=delete_url,
            is_file=True
        )
        discord_webhook.execute()

    # Return JSON
    return jsonify(
            {
                'url': file_url,
                'delete_url': delete_url
            }
        )

@api.route('/delete-file/<hmac_hash>/<filename>')
def delete_file(hmac_hash, filename):
    new_hmac_hash = utils.create_hmac_hash(filename, current_app.secret_key)

    # If hash does not match
    if utils.is_valid_hash(hmac_hash, new_hmac_hash) is False:
        return abort(404)

    if File.delete(filename) is False:
        return abort(404)

    message = render_template_string('{{ filename }} has been deleted, you can now close this page', filename=filename)
    return utils.response(message=message)

@api.route('/shorten', methods=['POST'])
@utils.auth_required
def shorten():
    url = request.form.get('url')

    if url is None:
        return utils.response(400, 'Invalid URL')

    short_url = ShortUrl(url)

    if short_url.is_valid() is False:
        return utils.response(400, 'Invalid URL')

    # Add URL to database
    short_url.add()

    # Create HMAC for URL using token
    token = short_url.get_token()
    hmac_hash = utils.create_hmac_hash(token, current_app.secret_key)

    # Create URLs
    short_url = url_for('main.short_url', token=token, _external=True)
    delete_url = url_for('api.delete_url', hmac_hash=hmac_hash, token=token, _external=True)

    # Send data to Discord webhook
    if discord_webhook.is_enabled:
        discord_webhook.embed(
            title='URL has been shortened!',
            description='{} => {}'.format(url, short_url),
            url=short_url,
            deletion_url=delete_url
        )
        discord_webhook.execute()

    return jsonify(
        {
            'url': short_url,
            'delete_url': delete_url
        }
    )

@api.route('/delete-short-url/<hmac_hash>/<token>')
def delete_url(hmac_hash, token):
    new_hmac_hash = utils.create_hmac_hash(token, current_app.secret_key)

    # If hash does not match
    if utils.is_valid_hash(hmac_hash, new_hmac_hash) is False:
        return abort(404)

    if ShortUrl.delete(token) is False:
        return abort(404)

    return utils.response(message='This short URL has been deleted, you can now close this page')
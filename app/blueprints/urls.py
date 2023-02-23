from http import HTTPStatus
from secrets import token_urlsafe

from flask import Blueprint, jsonify, url_for, abort, request

from app import config, logger
from app.core.utils import (
    auth_required, safe_str_comparison,
    create_hmac_hash
)
from app.core.discord import (
    create_short_url_embed,
    create_discord_webhooks,
    execute_webhooks_with_embed
)
from app.core.urls import (
    is_valid_url, 
    add_https_scheme_to_url,
    save_url_and_token_to_database, 
    delete_url_from_database_by_token
)

urls = Blueprint('urls', __name__)

@urls.get('/sharex/shorten')
def shorten_config():
    return jsonify({
        "Name": "{} (URL shortener)".format(request.host),
        "Version": "1.0.0",
        "DestinationType": "URLShortener",
        "RequestMethod": "POST",
        "Body": "MultipartFormData",
        "RequestURL": url_for('urls.shorten', _external=True),
        "Headers": {
            "Authorization": "YOUR-UPLOAD-PASSWORD-HERE"
        },
        "Arguments": {
            "url": "$input$"
        },
        "URL": "$json:url$",
        "ErrorMessage": "$json:status$"
    })

@urls.post('/shorten')
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
    deletion_url = url_for('urls.delete_short_url_with_hash', hmac_hash=hmac_hash, token=token, _external=True)

    logger.info(f'Saved short URL: {shortened_url} for {url}, deletion URL: {deletion_url}')

    # Send data to Discord webhooks
    discord_webhooks = create_discord_webhooks(config.discord_webhook_urls, config.discord_webhook_timeout)
    if discord_webhooks:
        embed = create_short_url_embed(url, shortened_url, deletion_url)
        execute_webhooks_with_embed(discord_webhooks, embed)

    return jsonify(url=shortened_url)

@urls.get('/delete-short-url/<hmac_hash>/<token>')
def delete_short_url_with_hash(hmac_hash, token):
    new_hmac_hash = create_hmac_hash(token, config.flask_secret)

    # If digest is invalid
    if safe_str_comparison(hmac_hash, new_hmac_hash) is False:
        abort(HTTPStatus.NOT_FOUND)

    if delete_url_from_database_by_token(token) is False:
        abort(HTTPStatus.GONE)

    return jsonify(message='This short URL has been deleted, you can now close this page.')

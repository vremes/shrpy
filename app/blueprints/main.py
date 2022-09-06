from http import HTTPStatus

from flask import Blueprint, jsonify, abort, redirect, send_from_directory

from app import config
from app.core.main import ShortUrl

main = Blueprint('main', __name__)

@main.get('/')
def index():
    return jsonify(message='It works! Beep boop.')

@main.get('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(config.upload.directory, filename)

@main.get('/url/<token>')
def short_url(token):
    short_url = ShortUrl.get_by_token(token)

    if short_url is None:
        abort(HTTPStatus.NOT_FOUND)

    return redirect(short_url)

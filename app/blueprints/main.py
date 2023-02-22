from http import HTTPStatus

from flask import Blueprint, jsonify, abort, redirect, send_from_directory

from app import config
from app.core.urls import get_url_by_token

main = Blueprint('main', __name__)

@main.get('/')
def index():
    return jsonify(message='It works! Beep boop.')

@main.get('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(config.upload_directory, filename)

@main.get('/url/<token>')
def short_url(token):
    url = get_url_by_token(token)
    if url is None:
        abort(HTTPStatus.NOT_FOUND)
    return redirect(url)

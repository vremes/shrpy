from app.helpers.urls import ShortUrl
from flask import Blueprint, send_from_directory, current_app, redirect, abort

main = Blueprint('main', __name__)

@main.route('/uploads/<filename>')
def uploads(filename):
    upload_dir = current_app.config['UPLOAD_DIR']

    return send_from_directory(upload_dir, filename)

@main.route('/url/<token>')
def short_url(token):
    short_url = ShortUrl.get_by_token(token)

    if short_url is None:
        abort(404)

    return redirect(short_url)
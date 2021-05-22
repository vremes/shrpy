from flask import Blueprint
from app.helpers.utils import auth_required
from app.helpers.services import FileService, ShortUrlService

api = Blueprint('api', __name__)

@api.route('/sharex/upload')
def upload_config():
    return FileService.config()

@api.route('/sharex/shorten')
def shorten_config():
    return ShortUrlService.config()

@api.route('/upload', methods=['POST'])
@auth_required
def upload():
    return FileService.create()

@api.route('/delete-file/<hmac_hash>/<filename>')
def delete_file(hmac_hash, filename):
    return FileService.delete()

@api.route('/shorten', methods=['POST'])
@auth_required
def shorten():
    return ShortUrlService.create()

@api.route('/delete-short-url/<hmac_hash>/<token>')
def delete_short_url(hmac_hash, token):
    return ShortUrlService.delete()
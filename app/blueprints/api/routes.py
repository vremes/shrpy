from flask import Blueprint
from app.helpers.utils import auth_required
from app.helpers.services import FileService, ShortUrlService

api = Blueprint('api', __name__)

@api.get('/sharex/upload')
def upload_config():
    return FileService.config()

@api.get('/sharex/shorten')
def shorten_config():
    return ShortUrlService.config()

@api.post('/upload')
@auth_required
def upload():
    return FileService.create()

@api.post('/shorten')
@auth_required
def shorten():
    return ShortUrlService.create()

@api.get('/delete-short-url/<hmac_hash>/<token>')
def delete_short_url(hmac_hash, token):
    return ShortUrlService.delete()

@api.get('/delete-file/<hmac_hash>/<filename>')
def delete_file(hmac_hash, filename):
    return FileService.delete()
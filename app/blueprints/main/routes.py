from flask import Blueprint
from app.helpers.services import ShortUrlService, FileService

main = Blueprint('main', __name__)

@main.get('/uploads/<filename>')
def uploads(filename):
    return FileService.get_by_filename()

@main.get('/url/<token>')
def short_url(token):
    return ShortUrlService.get_by_token()
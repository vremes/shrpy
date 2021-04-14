from flask import Blueprint
from app.helpers.services import ShortUrlService, FileService

main = Blueprint('main', __name__)

@main.route('/uploads/<filename>')
def uploads(filename):
    return FileService.get_by_filename(filename)

@main.route('/url/<token>')
def short_url(token):
    return ShortUrlService.get_by_token(token)
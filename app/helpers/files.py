import os
import hmac
import flask
import hashlib
import secrets
from app import config
from werkzeug.utils import secure_filename

def is_allowed_file(filename: str) -> bool:
    """
    Check if `filename`'s extension is allowed
    """
    _, ext = os.path.splitext(filename.lower())

    return ext in config.ALLOWED_EXTENSIONS

def get_modified_filename(filename: str, use_original_filename: bool = False) -> str:
    """
    Returns modified filename
    """
    fname, ext = os.path.splitext(filename.lower())
    secure_fname = secure_filename(fname)
    random_fname = secrets.token_urlsafe(12)

    if secure_fname and use_original_filename:
        secure_fname = secure_fname[:18]
        full_filename = '{}-{}{}'.format(random_fname, secure_fname, ext)
    else:
        full_filename = '{}{}'.format(random_fname, ext)

    return full_filename

def create_hmac_hash(secret, hmac_data) -> str:
    """
    Creates a hash using `hmac.new` and returns it

    :param str secret: The secret key for the hash
    :param str hmac_data: The message/input for the hash
    :return str hmac_hash HMAC hash
    """
    secret = secret.encode('utf-8')
    hmac_data = hmac_data.encode('utf-8')
    hmac_hash = hmac.new(secret, hmac_data,hashlib.sha256).hexdigest()
    return hmac_hash

def is_valid_hash(hash_a: str, hash_b: str) -> bool:
    """
    Compares two hashes using `hmac.compare_digest`
    """
    return hmac.compare_digest(hash_a, hash_b)

def sharex_config():
    """
    Returns the configuration for ShareX as dictionary
    """
    cfg = {
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

    return cfg
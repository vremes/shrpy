# standard library imports
import os
import hmac
import sqlite3
import logging
import hashlib
import mimetypes
from enum import Enum
from functools import wraps
from http import HTTPStatus
from logging.handlers import RotatingFileHandler

# pip imports
from flask import Response, jsonify, request, abort

# local imports
from app import config

def initialize_db():
    cursor = Database.get_instance()
    return cursor.execute("CREATE TABLE IF NOT EXISTS urls (token VARCHAR(10) NOT NULL PRIMARY KEY, url TEXT NOT NULL)")

def is_valid_digest(hash_a: str, hash_b: str) -> bool:
    """Compares two hashes using `hmac.compare_digest`."""
    return hmac.compare_digest(hash_a, hash_b)

def response(status_code: int = HTTPStatus.OK, status: str = HTTPStatus.OK.phrase, **kwargs) -> Response:
    """Wrapper for `flask.jsonify`

    :param int status_code: HTTP status code, defaults to `200`
    :param str status: HTTP status message or your own custom status, defaults to `OK`
    :param **kwargs: Arbitrary keyword arguments, these will be added to the returned `Response` as JSON key/value pairs
    :return flask.jsonify (flask.Response)
    """
    resp = jsonify(status_code=status_code, status=status, **kwargs)
    resp.status_code = status_code
    return resp

def auth_required(f):
    """Check HTTP `Authorization` header against the value of `config.UPLOAD_PASSWORD`, calls `flask.abort` if the password does not match."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if config.UPLOAD_PASSWORD:
            # Default to empty string if Authorization header is not sent
            authorization_header = request.headers.get('Authorization', default='')
            if not hmac.compare_digest(config.UPLOAD_PASSWORD, authorization_header):
                abort(HTTPStatus.UNAUTHORIZED)
        return f(*args, **kwargs)
    return decorated_function

def add_unsupported_mimetypes():
    """Adds unsupported mimetypes/extensions to `mimetypes` module."""
    for mime, ext in config.CUSTOM_EXTENSIONS.items():
        mime = mime.lower().strip()
        ext = f'.{ext.lower().strip()}'
        mimetypes.add_type(mime, ext)

def logger_handler() -> RotatingFileHandler:
    """Returns `logging.handlers.RotatingFileHandler` for logging."""
    if not os.path.isdir(config.LOGGER_FILE_PATH):
        os.makedirs(config.LOGGER_FILE_PATH)

    logfile_path = os.path.join(config.LOGGER_FILE_PATH, config.LOGGER_FILE_NAME)

    handler = RotatingFileHandler(logfile_path, maxBytes=config.LOGGER_MAX_BYTES, backupCount=config.LOGGER_BACKUP_COUNT)
    handler.setFormatter(
        logging.Formatter('%(asctime)s | %(module)s.%(funcName)s | %(levelname)s | %(message)s')
    )

    return handler

class Message(str, Enum):
    # Services
    INVALID_FILE = 'Invalid file'
    INVALID_FILE_TYPE = 'Invalid file type'
    FILE_DELETED = 'This file has been deleted, you can now close this page'

    INVALID_URL = 'Invalid URL'
    URL_DELETED = 'This short URL has been deleted, you can now close this page'

    # Embeds
    URL = 'URL'
    DELETION_URL = 'Deletion URL'
    CLICK_HERE_TO_VIEW = 'Click here to view'
    CLICK_HERE_TO_DELETE = 'Click here to delete'

    FILE_UPLOADED = 'New file has been uploaded!'
    URL_SHORTENED = 'URL has been shortened!'

class HMAC:
    """
    Utility class for HMAC.
    """
    hmac_payload = None
    hmac_secret = None

    __hmac = None
    __digest = hashlib.sha256

    def __init__(self, payload: str = None, secret: str = None):
        self.hmac_payload = payload or ''
        self.hmac_secret = secret or ''

    def create_hmac(self) -> hmac.HMAC:
        self.__hmac = hmac.new(
            self.hmac_secret.encode('utf-8'),
            self.hmac_payload.encode('utf-8'),
            self.__digest
        )
        return self.__hmac

    def hmac_hexdigest(self) -> str:
        if self.__hmac is None:
            self.create_hmac()
        return self.__hmac.hexdigest()

class Database:
    """
    Database singleton.
    """
    __connection = None

    @classmethod
    def get_instance(cls) -> sqlite3.Cursor:
        if cls.__connection is None:
            cls.__connection = sqlite3.connect('urls.db', check_same_thread=False)

            # Enable autocommit & change row factory
            cls.__connection.isolation_level = None
            cls.__connection.row_factory = sqlite3.Row

            cls.cursor = cls.__connection.cursor()

        return cls.cursor
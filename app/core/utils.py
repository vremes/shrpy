# standard library imports
from enum import Enum
from pathlib import Path
from hashlib import sha256
from functools import wraps
from http import HTTPStatus
from mimetypes import add_type
from hmac import compare_digest, new
from sqlite3 import Cursor, Row, connect
from logging import Formatter
from logging.handlers import RotatingFileHandler

# pip imports
from flask import Response, jsonify, request, abort

# local imports
from app import config

def initialize_db():
    cursor = Database.get_instance()
    return cursor.execute("CREATE TABLE IF NOT EXISTS urls (token VARCHAR(10) NOT NULL PRIMARY KEY, url TEXT NOT NULL)")

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
            if not compare_digest(config.UPLOAD_PASSWORD, authorization_header):
                abort(HTTPStatus.UNAUTHORIZED)
        return f(*args, **kwargs)
    return decorated_function

def add_unsupported_mimetypes():
    """Adds unsupported mimetypes/extensions to `mimetypes` module."""
    for mime, ext in config.CUSTOM_EXTENSIONS.items():
        mime = mime.lower().strip()
        ext = f'.{ext.lower().strip()}'
        add_type(mime, ext)

def logger_handler() -> RotatingFileHandler:
    """Returns `logging.handlers.RotatingFileHandler` for logging."""
    path = Path(config.LOGGER_FILE_PATH)

    if path.exists() is False:
        path.mkdir()

    logfile_path = path / config.LOGGER_FILE_NAME

    handler = RotatingFileHandler(logfile_path, maxBytes=config.LOGGER_MAX_BYTES, backupCount=config.LOGGER_BACKUP_COUNT)
    handler.setFormatter(
        Formatter('%(asctime)s | %(module)s.%(funcName)s | %(levelname)s | %(message)s')
    )

    return handler

def create_hmac_hash(hmac_payload: str, hmac_secret_key: str) -> str:
    """Returns sha256 HMAC hexdigest."""
    return new(
        hmac_secret_key.encode('utf-8'),
        hmac_payload.encode('utf-8'),
        sha256
    ).hexdigest()

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

class Database:
    """
    Database singleton.
    """
    __connection = None

    @classmethod
    def get_instance(cls) -> Cursor:
        if cls.__connection is None:
            cls.__connection = connect('urls.db', check_same_thread=False)

            # Enable autocommit & change row factory
            cls.__connection.isolation_level = None
            cls.__connection.row_factory = Row

            cls.cursor = cls.__connection.cursor()

        return cls.cursor
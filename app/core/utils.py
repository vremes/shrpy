# standard library imports
from sys import stdout
from hashlib import sha256
from functools import wraps
from http import HTTPStatus
from mimetypes import add_type
from hmac import compare_digest, new
from sqlite3 import Row, connect
from logging import Formatter, StreamHandler

# pip imports
from werkzeug.exceptions import HTTPException
from flask import Response, jsonify, abort, request

# local imports
from app import config

def http_error_handler(exception: HTTPException, **kwargs) -> Response:
    """Error handler for `werkzeug.exceptions.HTTPException`.

    Args:
        exception (HTTPException): HTTPException instance

    Returns:
        Response: flask.Response
    """
    response = jsonify(
        status_code=exception.code,
        status=exception.description,
        **kwargs
    )
    response.status_code = exception.code
    return response

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

def logger_handler() -> StreamHandler:
    """Returns stdout handler for logging."""
    handler = StreamHandler(stdout)
    handler.setFormatter(
        Formatter('%(asctime)s | %(module)s.%(funcName)s | %(levelname)s | %(message)s')
    )
    return handler

def create_hmac_hash(hmac_payload: str, hmac_secret_key: str) -> str:
    """Returns sha256 HMAC hexdigest."""

    if hmac_secret_key is None:
        raise RuntimeError('hmac_secret_key cannot be None, please set a secret for the application in dotenv file!')

    return new(
        hmac_secret_key.encode('utf-8'),
        hmac_payload.encode('utf-8'),
        sha256
    ).hexdigest()

def setup_db():
    """Connects to SQLite3 database and returns the connection cursor."""
    connection = connect('shrpy.db', check_same_thread=False)
    connection.isolation_level = None
    connection.row_factory = Row

    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS urls (token VARCHAR(10) NOT NULL PRIMARY KEY, url TEXT NOT NULL)")

    return cursor

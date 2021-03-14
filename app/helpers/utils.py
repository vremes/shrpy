import hmac
import flask
import hashlib
from app import config
from random import randint
from functools import wraps
from http import HTTPStatus
from werkzeug.security import safe_str_cmp

def create_hmac_hash(hmac_data: str, secret_key: str = None) -> str:
    """Creates HMAC hash using the hmac_data and returns it."""
    hmac_hash = hmac.new(
        secret_key.encode('utf-8'),
        hmac_data.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return hmac_hash

def is_valid_hash(hash_a: str, hash_b: str) -> bool:
    """Compares two hashes using `hmac.compare_digest`."""
    return hmac.compare_digest(hash_a, hash_b)

def response(status_code: int = 200, status: str = "OK", **kwargs) -> flask.Response:
    """Wrapper for `flask.jsonify`

    :param int status_code: HTTP status code, defaults to `200`
    :param str status: HTTP status message or your own custom status, defaults to `OK`
    :param **kwargs: Arbitrary keyword arguments, these will be added to the returned `Response` as JSON key/value pairs
    :return flask.jsonify (flask.Response)
    """
    response_dict = {
        "status_code": status_code,
        "status": status,
    }

    for key, value in kwargs.items():
        response_dict[key] = value

    resp = flask.jsonify(response_dict)
    resp.status_code = status_code

    return resp

def auth_required(f):
    """Check HTTP `Authorization` header against the value of `config.UPLOAD_PASSWORD`, calls `flask.abort` if the password does not match."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if config.UPLOAD_PASSWORD is not None:
            authorization_header = flask.request.headers.get('Authorization')
            if authorization_header is None or safe_str_cmp(config.UPLOAD_PASSWORD, authorization_header) is False:
                return flask.abort(HTTPStatus.UNAUTHORIZED)
        return f(*args, **kwargs)
    return decorated_function

def random_hex():
    return randint(0, 0xffffff)
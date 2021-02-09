from app import config
from functools import wraps
from flask import request, abort
from werkzeug.security import safe_str_cmp

def auth_required(f):
    """Check HTTP `Authorization` header against the value of `config.UPLOAD_PASSWORD`, calls `flask.abort` if the password does not match."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if config.UPLOAD_PASSWORD is not None:
            authorization_header = request.headers.get('Authorization')
            if authorization_header is None or safe_str_cmp(config.UPLOAD_PASSWORD, authorization_header) is False:
                return abort(401)
        return f(*args, **kwargs)
    return decorated_function
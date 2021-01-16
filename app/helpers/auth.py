from app import config
from functools import wraps
from flask import request, abort

def auth_required(f):
    """
    Check HTTP `Authorization` header against the value of `config.UPLOAD_PASSWORD`, calls `flask.abort` if the password does not match.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if config.UPLOAD_PASSWORD is not None:
            authorization_header = request.headers.get('Authorization')
            if authorization_header != config.UPLOAD_PASSWORD:
                return abort(401)
        return f(*args, **kwargs)
    return decorated_function
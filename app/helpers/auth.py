from app import config
from functools import wraps
from flask import current_app, request, redirect, url_for, abort

def auth_required(f):
    """
    Check HTTP `Authorization` header against the value of `config.UPLOAD_PASSWORD`
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if config.UPLOAD_PASSWORD is not None:
            authorization_header = request.headers.get('Authorization')
            if authorization_header != config.UPLOAD_PASSWORD:
                return abort(401)
        return f(*args, **kwargs)
    return decorated_function
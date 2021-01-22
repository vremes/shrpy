import os
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
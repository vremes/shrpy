from pathlib import Path, PurePath

from uuid import uuid4
from mimetypes import add_type
from werkzeug.utils import secure_filename
from python_magic_file import MagicFile

def is_file_extension_allowed(file_extension: str , allowed_file_extensions: list) -> bool:
    """Returns True if given file_extension is allowed."""
    extension_without_dot = file_extension.replace('.', '')
    return extension_without_dot in allowed_file_extensions

def delete_file(file_path: str) -> bool:
    """Deletes a given file if it exists."""
    path = Path(file_path)
    if path.is_file() is False:
        return False
    path.unlink()
    return True

def get_secure_filename(arbitrary_filename: str) -> str:
    """Returns secure version if given arbitrary_filename."""
    filename = secure_filename(arbitrary_filename)
    return PurePath(filename).stem

def generate_filename() -> str:
    """Returns a random filename."""
    return str(uuid4())

def get_file_extension_from_file(file_like_object, buffer: int = 2048) -> str | None:
    """Returns file extension from file-like object."""
    magic_file = MagicFile(file_like_object)
    return magic_file.get_extension(buffer)

def create_directory(directory: str) -> None:
    """Creates a given directory."""
    return Path(directory).mkdir(exist_ok=True)

def add_unsupported_mimetypes(mimetypes_map: dict[str, str]):
    """Adds unsupported mimetypes/extensions to `mimetypes` module."""
    for mime, ext in mimetypes_map.items():
        mime = mime.lower().strip()
        ext = f'.{ext.lower().strip()}'
        add_type(mime, ext)

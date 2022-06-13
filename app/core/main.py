# standard library imports
from os import SEEK_SET
from dataclasses import dataclass
from secrets import token_urlsafe
from urllib.parse import urlparse
from pathlib import Path, PurePath
from functools import cached_property
from mimetypes import guess_extension

# pip imports
from magic import from_buffer
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

# local imports
from app import db
from app.config import UploadedFileConfig, ShortUrlConfig
from app.core.utils import create_hmac_hash

@dataclass(frozen=True)
class UploadedFile:
    """Represents uploaded file."""
    filename: str
    extension: str
    config: UploadedFileConfig

    def is_allowed(self) -> bool:
        """Check if file is allowed, based on `config.allowed_extensions`."""
        if not self.extension:
            return False
        ext_without_dot = self.extension.replace('.', '')
        return ext_without_dot in self.config.allowed_extensions

    def generate_filename_hmac(self, secret: str) -> str:
        """Generates HMAC from filename and extension."""
        return create_hmac_hash(self.full_filename, secret)

    @cached_property
    def full_filename(self) -> str:
        """Filename and extension as a string."""
        return self.filename + self.extension

    @staticmethod
    def delete(file_path: str) -> bool:
        """Deletes a file from upload directory"""
        path = Path(file_path)

        if path.is_file() is False:
            return False

        path.unlink()

        return True

    @classmethod
    def from_file_storage_instance(cls, file_storage_instance: FileStorage, config: UploadedFileConfig):
        """Builds FileData instance from werkzeug.datastructures.FileStorage instance."""
        filename = token_urlsafe(config.file_token_bytes)

        if config.use_original_filename:
            original_filename_safe = PurePath(secure_filename(file_storage_instance.filename)).stem
            original_filename_shortened = original_filename_safe[:config.original_filename_length]
            filename = f'{filename}-{original_filename_shortened}'

        file_bytes = file_storage_instance.read(config.magic_buffer_bytes)
        file_storage_instance.seek(SEEK_SET)

        mime = from_buffer(file_bytes, mime=True).lower()
        extension = guess_extension(mime)

        return cls(filename, extension, config)

@dataclass(frozen=True)
class ShortUrl:
    url: str
    token: str

    def is_valid(self) -> bool:
        """Checks if URL is valid"""
        parsed = urlparse(self.url)
        return all([parsed.scheme, parsed.netloc])

    def save_to_database(self):
        """Inserts the URL and token to database."""
        db.execute("INSERT INTO urls VALUES (?, ?)", (
            self.token,
            self.url
        ))

    def generate_token_hmac(self, secret: str) -> str:
        """Generates HMAC from token."""
        return create_hmac_hash(self.token, secret)

    @staticmethod
    def get_by_token(token: str):
        """Returns the URL for given token from database."""
        query = db.execute("SELECT url FROM urls WHERE token = ? LIMIT 1", (token,))
        row = query.fetchone()
        if not row:
            return None
        return row['url']

    @staticmethod
    def delete_by_token(token: str) -> bool:
        """DELETEs URL using given token from database."""
        execute = db.execute("DELETE FROM urls WHERE token = ?", (token,))
        return execute.rowcount > 0

    @classmethod
    def from_url(cls, url: str, config: ShortUrlConfig):
        """Creates ShortUrl instance from given URL."""
        token = token_urlsafe(config.url_token_bytes)

        if not url.lower().startswith(('https://', 'http://')):
            url = f'https://{url}'

        return cls(url, token)

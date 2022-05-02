# standard library imports
from os import SEEK_SET
from secrets import token_urlsafe
from urllib.parse import urlparse
from pathlib import Path, PurePath
from functools import cached_property
from mimetypes import guess_extension

# pip imports
from magic import from_buffer
from werkzeug.datastructures import FileStorage
from werkzeug.utils import safe_join, secure_filename

# local imports
from app import config, db

class File:
    def __init__(self, file_storage: FileStorage):
        if isinstance(file_storage, FileStorage) is False:
            raise InvalidFileException(file_storage)

        self.__file = file_storage

        # Get filename using PurePath and make sure filename is safe by using secure_filename
        self.__filename = PurePath(
            secure_filename(self.__file.filename)
        ).stem

        self.use_original_filename = True

    @cached_property
    def root(self) -> str:
        """Returns filename root for the file."""
        filename = token_urlsafe(config.FILE_TOKEN_BYTES)

        if self.use_original_filename:
            original_filename_shortened = self.__filename[:config.ORIGINAL_FILENAME_LENGTH]
            filename =  f'{filename}-{original_filename_shortened}'

        return filename

    @cached_property
    def extension(self) -> str:
        """Returns guessed extension for the file."""
        file_bytes = self.__file.read(config.MAGIC_BUFFER_BYTES)
        mime = from_buffer(file_bytes, mime=True).lower()
        ext = guess_extension(mime)

        if not ext:
            return None

        return ext.replace('.', '')

    @cached_property
    def filename(self):
        return f'{self.root}.{self.extension}'

    def is_allowed(self) -> bool:
        """Check if file is allowed, based on `config.ALLOWED_EXTENSIONS`."""
        if not self.extension:
            return False
        return self.extension in config.ALLOWED_EXTENSIONS

    def save(self, save_directory = config.UPLOAD_DIR) -> None:
        """Saves the file to `UPLOAD_DIR`."""
        path = Path(save_directory)

        if path.exists() is False:
            path.mkdir()

        save_path = safe_join(save_directory, self.filename)

        # Set file descriptor back to beginning of the file so save works correctly
        self.__file.seek(SEEK_SET)

        return self.__file.save(save_path)

    @staticmethod
    def delete(filename: str) -> bool:
        """Deletes the file from `config.UPLOAD_DIR`, if it exists."""
        file_path = safe_join(config.UPLOAD_DIR, filename)
        path = Path(file_path)

        if path.is_file() is False:
            return False

        path.unlink()

        return True

class InvalidFileException(Exception):
    """Raised when `File` is initialized using wrong `file_instance`."""
    def __init__(self, file_instance, *args):
        self.file_instance = file_instance
        super().__init__(*args)

    def __str__(self):
        file_instance_type = type(self.file_instance)
        return f'{self.file_instance} ({file_instance_type}) is not an instance of werkzeug.datastructures.FileStorage ({FileStorage})'

class ShortUrl:
    def __init__(self, url: str):
        if not url.lower().startswith(('https://', 'http://')):
            url = f'https://{url}'

        self.url = url

    @cached_property
    def token(self) -> str:
        return token_urlsafe(config.URL_TOKEN_BYTES)

    def is_valid(self) -> bool:
        """Checks if URL is valid"""
        parsed = urlparse(self.url)

        # Parsed URL must have at least scheme and netloc (e.g. domain name)
        try:
            valid = all([parsed.scheme, parsed.netloc]) and parsed.netloc.split('.')[1]
        except IndexError:
            valid = False

        return valid

    def add(self):
        """Inserts the URL and token to database."""
        db.execute("INSERT INTO urls VALUES (?, ?)", (
            self.token,
            self.url
        ))

    @staticmethod
    def get_by_token(token: str):
        """Returns the URL for given token from database."""
        result = None

        row = db.execute("SELECT url FROM urls WHERE token = ?", (token,))
        url_row = row.fetchone()
        if url_row:
            result = url_row['url']
        return result

    @staticmethod
    def delete(token: str) -> bool:
        """DELETEs URL using given token from database."""
        execute = db.execute("DELETE FROM urls WHERE token = ?", (token,))
        deleted = execute.rowcount > 0

        return deleted

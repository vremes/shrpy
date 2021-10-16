# standard library imports
import os
import secrets
import sqlite3
from urllib.parse import urlparse
from functools import cached_property
from mimetypes import guess_extension

# pip imports
from magic import from_buffer
from flask import url_for, current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import safe_join, secure_filename

# local imports
from app import config
from app.helpers.utils import create_hmac_hexdigest
from app.helpers.discord import FileEmbed, ShortUrlEmbed

class File:
    def __init__(self, file_storage: FileStorage):
        if isinstance(file_storage, FileStorage) is False:
            raise InvalidFileException(file_storage)

        self.__file = file_storage

        # splitext returns tuple
        # make sure filename is safe by using secure_filename
        self.__filename, self.__extension = os.path.splitext(
            secure_filename(self.__file.filename)
        )

        self.use_original_filename = True
    
    @cached_property
    def root(self) -> str:
        """Returns filename root for the file."""
        filename = secrets.token_urlsafe(config.FILE_TOKEN_BYTES)

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

        if ext is None:
            current_app.logger.error(f'Unable to determine file extension for file {self.__file.filename} - MIME type {mime}')
            return None

        ext = ext.lower().replace('.', '')
        return ext

    @cached_property
    def filename(self):
        return f'{self.root}.{self.extension}'

    @cached_property
    def hmac(self) -> str:
        """Returns HMAC digest calculated from filename, `flask.current_app.secret_key` is used as secret."""
        return create_hmac_hexdigest(self.filename, current_app.secret_key)

    @cached_property
    def url(self) -> str:
        """Returns file URL using `flask.url_for`."""
        return url_for('main.uploads', filename=self.filename, _external=True)

    @cached_property
    def deletion_url(self) -> str:
        """Returns deletion URL using `flask.url_for`."""
        return url_for('api.delete_file', hmac_hash=self.hmac, filename=self.filename, _external=True)

    def is_allowed(self) -> bool:
        """Check if file is allowed, based on `config.ALLOWED_EXTENSIONS`."""
        if not self.extension:
            return False

        if not config.ALLOWED_EXTENSIONS:
            return True
        
        allowed = self.extension in config.ALLOWED_EXTENSIONS

        if allowed is False:
            current_app.logger.warning(f'File {self.__file.filename} (detected extension {self.extension}) is not allowed')        

        return allowed

    def save(self, save_directory = config.UPLOAD_DIR) -> None:
        """Saves the file to `UPLOAD_DIR`."""
        if os.path.isdir(save_directory) is False:
            os.makedirs(save_directory)

        save_path = safe_join(save_directory, self.filename)

        current_app.logger.info(f'Saving file {self.__file.filename} to {save_path}')
        current_app.logger.info(f'URLs: {self.url} - {self.deletion_url}')

        # Set file descriptor back to beginning of the file so save works correctly
        self.__file.seek(os.SEEK_SET)

        return self.__file.save(save_path)

    def embed(self) -> FileEmbed:
        """Returns FileEmbed instance for this file."""
        return FileEmbed(
            content_url=self.url, 
            deletion_url=self.deletion_url
        )

    @staticmethod
    def delete(filename: str) -> bool:
        """Deletes the file from `config.UPLOAD_DIR`, if it exists."""
        file_path = safe_join(config.UPLOAD_DIR, filename)

        if os.path.isfile(file_path) is False:
            return False

        current_app.logger.info(f'Deleted file {file_path}')

        os.remove(file_path)

        return True

class InvalidFileException(Exception):
    """Raised when `File` is initialized using wrong `file_instance`."""
    def __init__(self, file_instance, *args):
        self.file_instance = file_instance
        super().__init__(*args)

    def __str__(self):
        file_instance_type = type(self.file_instance)
        return f'{self.file_instance} ({file_instance_type}) is not an instance of werkzeug.datastructures.FileStorage ({FileStorage})'


class Database:
    __connection = None

    @classmethod
    def get_instance(cls) -> sqlite3.Cursor:
        if cls.__connection is None:
            cls.__connection = sqlite3.connect('urls.db', check_same_thread=False)

            # Enable autocommit & change row factory
            cls.__connection.isolation_level = None
            cls.__connection.row_factory = sqlite3.Row

            # Create default DB and setup cursor
            cls.__connection.execute("CREATE TABLE IF NOT EXISTS urls (token VARCHAR(10) NOT NULL PRIMARY KEY, url TEXT NOT NULL)")
            cls.cursor = cls.__connection.cursor()

        return cls.cursor

class ShortUrl:
    def __init__(self, url: str):
        if not url.lower().startswith(('https://', 'http://')):
            url = f'https://{url}'

        self.url = url

    @cached_property
    def token(self) -> str:
        return secrets.token_urlsafe(config.URL_TOKEN_BYTES)

    @cached_property
    def hmac(self) -> str:
        """Returns HMAC hash calculated from token, `flask.current_app.secret_key` is used as secret."""
        return create_hmac_hexdigest(self.token, current_app.secret_key)

    @cached_property
    def shortened_url(self) -> str:
        """Returns the shortened URL using `flask.url_for`."""
        return url_for('main.short_url', token=self.token, _external=True)

    @cached_property
    def deletion_url(self) -> str:
        """Returns deletion URL using `flask.url_for`."""
        return url_for('api.delete_short_url', hmac_hash=self.hmac, token=self.token, _external=True)

    def is_valid(self) -> bool:
        """Checks if URL is valid"""
        parsed = urlparse(self.url)

        # Parsed URL must have at least scheme and netloc (e.g. domain name)
        try:
            valid = all([parsed.scheme, parsed.netloc]) and parsed.netloc.split('.')[1]
        except IndexError:
            valid = False

        if valid is False:
            current_app.logger.warning(f'URL {self.url} is invalid')

        return valid

    def add(self):
        """Inserts the URL and token to database."""

        current_app.logger.info(f'Saving short URL for {self.url} as {self.shortened_url}')
        current_app.logger.info(f'URLs: {self.shortened_url} - {self.deletion_url}')

        cursor = Database.get_instance()

        cursor.execute("INSERT INTO urls VALUES (?, ?)", (
            self.token,
            self.url
        ))

    def embed(self) -> ShortUrlEmbed:
        """Returns ShorturlEmbed instance for this URL."""
        return ShortUrlEmbed(
            content_url=self.shortened_url, 
            deletion_url=self.deletion_url, 
            original_url=self.url, 
            shortened_url=self.shortened_url
        )

    @classmethod
    def get_by_token(cls, token: str):
        """Returns the URL for given token from database."""
        result = None
        
        cursor = Database.get_instance()
        row = cursor.execute("SELECT url FROM urls WHERE token = ?", (token,))
        url_row = row.fetchone()
        if url_row:
            result = url_row['url']
        return result

    @classmethod
    def delete(cls, token: str) -> bool:
        """DELETEs URL using given token from database."""

        url = cls.get_by_token(token)

        cursor = Database.get_instance()
        execute = cursor.execute("DELETE FROM urls WHERE token = ?", (token,))
        deleted = execute.rowcount > 0

        if deleted:
            current_app.logger.info(f'Deleted short URL for {url} using token {token}')

        return deleted


import os
import magic
import secrets
import mimetypes
from app import config
from app.helpers import utils
from flask import current_app, url_for
from functools import cached_property
from werkzeug.security import safe_join
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from app.helpers.discord.embeds import FileEmbed

class File:
    def __init__(self, file_instance: FileStorage, use_original_filename=True):
        """Class for uploaded files which takes the `werkzeug.datastructures.FileStorage` from `flask.Request.files` as first parameter."""
        if isinstance(file_instance, FileStorage) is False:
            raise InvalidFileException(file_instance)

        self.use_original_filename = use_original_filename

        # Private FileStorage instance
        self.__file = file_instance

    @cached_property
    def filename(self) -> str:
        """Returns random filename."""
        custom_filename = secrets.token_urlsafe(config.FILE_TOKEN_BYTES)

        if self.use_original_filename:
            filename = f'{custom_filename}-{self.original_filename_root[:18]}'
        else:
            filename = custom_filename

        return f'{filename}{self.extension}'

    @cached_property
    def extension(self) -> str:
        """Returns extension using `python-magic` and `mimetypes`."""
        file_bytes = self.__file.read(config.MAGIC_BUFFER_BYTES)
        mime = magic.from_buffer(file_bytes, mime=True).lower()

        self.add_custom_mimetypes()

        return mimetypes.guess_extension(mime)

    @cached_property
    def original_filename_root(self):
        """Returns the original filename without extension."""
        sec_filename = secure_filename(self.__file.filename.lower())
        root, ext = os.path.splitext(sec_filename)
        return root

    @cached_property
    def hmac(self) -> str:
        """Returns HMAC hash calculated from filename, `flask.current_app.secret_key` is used as secret."""
        return utils.create_hmac_hash(self.filename, current_app.secret_key)
    
    @cached_property
    def url(self) -> str:
        """Returns file URL using `flask.url_for`."""
        return url_for('main.uploads', filename=self.filename, _external=True)
    
    @cached_property
    def deletion_url(self) -> str:
        """Returns deletion URL using `flask.url_for`."""
        return url_for('api.delete_file', hmac_hash=self.hmac, filename=self.filename, _external=True)

    @staticmethod
    def delete(filename: str) -> bool:
        """Deletes the file from `config.UPLOAD_DIR`, if it exists."""
        file_path = safe_join(config.UPLOAD_DIR, filename)

        if os.path.isfile(file_path) is False:
            return False

        os.remove(file_path)

        return True

    def is_allowed(self) -> bool:
        """Check if file is allowed, based on `config.ALLOWED_EXTENSIONS`."""
        if not config.ALLOWED_EXTENSIONS:
            return True

        return self.extension in config.ALLOWED_EXTENSIONS

    def save(self, save_directory = config.UPLOAD_DIR) -> None:
        """Saves the file to `UPLOAD_DIR`."""
        if os.path.isdir(save_directory) is False:
            os.makedirs(save_directory)

        save_path = safe_join(save_directory, self.filename)

        # Set file descriptor back to beginning of the file so save works correctly
        self.__file.seek(os.SEEK_SET)

        self.__file.save(save_path)

    def add_custom_mimetypes(self):
        """Adds unsupported mimetypes/extensions to `mimetypes` module."""
        mimetypes.add_type('video/x-m4v', '.m4v')

    def embed(self) -> FileEmbed:
        """Returns FileEmbed instance for this file."""
        embed = FileEmbed(
            content_url=self.url, 
            deletion_url=self.deletion_url
        )
        return embed

class InvalidFileException(Exception):
    """Raised when `app.helpers.files.File` is initialized using wrong `file_instance`."""
    def __init__(self, file_instance, *args):
        self.file_instance = file_instance
        super().__init__(*args)

    def __str__(self):
        file_instance_type = type(self.file_instance)
        return f'{self.file_instance} ({file_instance_type}) is not an instance of werkzeug.datastructures.FileStorage ({FileStorage})'

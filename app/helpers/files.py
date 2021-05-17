import os
import magic
import secrets
import mimetypes
from app import config
from werkzeug.security import safe_join
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

class File:
    def __init__(self, file_instance: FileStorage):
        """Class for uploaded files which takes the `werkzeug.datastructures.FileStorage` from `flask.Request.files` as first parameter."""
        if isinstance(file_instance, FileStorage) is False:
            raise InvalidFileException(file_instance)

        self.use_original_filename = False

        # Private FileStorage instance
        self.__file = file_instance

        # Set arbitrary FileStorage.filename to lowercase and secure version of itself
        self.__file.filename = secure_filename(self.__file.filename.lower())

        # Setup extension and filename
        self.__set_extension()
        self.__set_filename()

    @property
    def filename(self) -> str:
        return self.__filename
    
    @property
    def extension(self) -> str:
        return self.__extension

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

    def __set_filename(self):
        custom_filename = secrets.token_urlsafe(config.FILE_TOKEN_BYTES)

        if self.use_original_filename:
            filename = f'{custom_filename}-{self.__file.filename[:18]}'
        else:
            filename = custom_filename

        self.__filename = f'{filename}{self.extension}'

    def __set_extension(self):
        file_bytes = self.__file.read(config.MAGIC_BUFFER_BYTES)
        mime = magic.from_buffer(file_bytes, mime=True).lower()
        self.__extension = mimetypes.guess_extension(mime)

class InvalidFileException(Exception):
    """Raised when `app.helpers.files.File` is initialized using wrong `file_instance`."""
    def __init__(self, file_instance, *args):
        self.file_instance = file_instance
        super().__init__(*args)

    def __str__(self):
        file_instance_type = type(self.file_instance)
        return f'{self.file_instance} ({file_instance_type}) is not an instance of werkzeug.datastructures.FileStorage ({FileStorage})'

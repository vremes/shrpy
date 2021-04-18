import os
import secrets
from app import config
from werkzeug.security import safe_join
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

class File:
    def __init__(self, file_instance: FileStorage):
        """Class for uploaded files which takes the `werkzeug.datastructures.FileStorage` from `flask.Request.files` as first parameter."""
        if isinstance(file_instance, FileStorage) is False:
            raise Exception("file_instance should be instance of FileStorage from flask.Request.files")

        self.custom_filename = None
        self.use_original_filename = False

        # Private FileStorage instance
        self.__file = file_instance

        # Set arbitrary FileStorage.filename to lowercase and secure version of itself
        self.__file.filename = secure_filename(self.__file.filename.lower())

        # Split filename to tuple (filename, ext) and assign them to variables
        self.filename, self.extension = os.path.splitext(self.__file.filename)

    def get_filename(self) -> str:
        """Returns custom filename, generated using `secrets.token_urlsafe`."""
        if self.custom_filename is None:
            custom_filename = secrets.token_urlsafe(12)

            if self.use_original_filename:
                self.custom_filename = '{}-{}{}'.format(custom_filename, self.filename[:18], self.extension)
            else:
                self.custom_filename = '{}{}'.format(custom_filename, self.extension)

        return self.custom_filename

    def is_allowed(self) -> bool:
        """Check if file is allowed, based on `config.ALLOWED_EXTENSIONS`."""
        if not config.ALLOWED_EXTENSIONS:
            return True
        return self.extension in config.ALLOWED_EXTENSIONS

    def save(self, save_directory = config.UPLOAD_DIR) -> None:
        """Saves the file to `UPLOAD_DIR`."""
        if os.path.isdir(save_directory) is False:
            os.makedirs(save_directory)

        save_path = safe_join(save_directory, self.get_filename())
        self.__file.save(save_path)

    @staticmethod
    def delete(filename: str) -> bool:
        """Deletes the file from `config.UPLOAD_DIR`, if it exists."""
        file_path = safe_join(config.UPLOAD_DIR, filename)

        if os.path.isfile(file_path) is False:
            return False

        os.remove(file_path)

        return True
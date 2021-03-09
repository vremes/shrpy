import os
import datetime
from app import config
from apscheduler.schedulers.background import BackgroundScheduler

class FileDeletionScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.upload_directory = config.UPLOAD_DIR
        self.days_threshold = config.DELETE_THRESHOLD_DAYS
        self.file_extensions_tuple = tuple(config.ALLOWED_EXTENSIONS)

    def get_files(self) -> list:
        """Returns a list of files from `config.UPLOAD_DIR` that match `config.ALLOWED_EXTENSIONS`"""
        files = []

        # Loop through all files in upload directory
        for f in os.listdir(self.upload_directory):

            # Make sure file is actually a file (not a directory!)
            file_path = os.path.join(self.upload_directory, f)
            if os.path.isfile(file_path) is False:
                continue
            
            # If file uses wrong extension, skip it
            if f.lower().endswith(self.file_extensions_tuple) is False:
                continue

            # Everything is OK, append the file to our list
            files.append(file_path)

        return files

    def get_stale_files(self) -> list:
        """Returns a list of files that are older than `config.DELETE_THRESHOLD_DAYS`."""
        stale_files = []
        files = self.get_files()

        if len(files) == 0:
            return stale_files

        current_date = datetime.datetime.today()

        # Loop through files and check if modification date difference exceeds threshold
        for f in files:
            file_modification_time = os.path.getmtime(f)
            file_modification_date = datetime.datetime.fromtimestamp(file_modification_time)

            date_difference = current_date - file_modification_date

            if date_difference.days >= self.days_threshold:
                stale_files.append(f)

        return stale_files

    def delete_stale_files(self):
        """Deletes files returned by `FileDeletionScheduler.get_stale_files()`."""
        stale_files = self.get_stale_files()

        for stale_file in stale_files:
            os.remove(stale_file)

    def setup(self):
        """Adds `delete_stale_files` job to scheduler and calls `scheduler.start()`."""
        if isinstance(self.days_threshold, int) is False or self.days_threshold == 0:
            return

        if os.path.isdir(self.upload_directory) is False:
            os.makedirs(self.upload_directory)

        self.scheduler.add_job(func=self.delete_stale_files, trigger='interval', minutes=60)
        self.scheduler.start()

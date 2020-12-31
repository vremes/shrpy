import os
import datetime
from app import config
from apscheduler.schedulers.background import BackgroundScheduler

def get_stale_files():
    """
    Returns a list of files that are older than `config.DELETE_THRESHOLD_DAYS`.
    """
    days_threshold = config.DELETE_THRESHOLD_DAYS
    upload_directory = config.UPLOAD_DIR
    stale_files = []

    if days_threshold == 0:
        return stale_files

    file_list = os.listdir(upload_directory)

    if len(file_list) == 0:
        return stale_files

    current_date = datetime.datetime.today()

    for f in file_list:
        file_path = os.path.join(upload_directory, f)
        file_modification_time = os.path.getmtime(file_path)
        file_modification_date = datetime.datetime.fromtimestamp(file_modification_time)
        
        date_difference = current_date - file_modification_date

        if date_difference.days >= days_threshold:
            stale_files.append(file_path)

    return stale_files

def delete_stale_files():
    """
    Deletes files returned by `delete_files.get_stale_files()`
    """
    stale_files = get_stale_files()

    for stale_file in stale_files:
        os.remove(stale_file)

def setup_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=delete_stale_files, trigger='interval', minutes=60)
    scheduler.start()
import os

# Maximum upload file size (~16mb)
# Example: https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/#improving-uploads
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Path for uploaded files
UPLOAD_DIR = os.path.join(os.getcwd(), 'app', 'uploads')

# List of allowed file extensions
ALLOWED_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.webm', '.mp4', '.webp', '.txt']

# Password for file uploads, leave it to None if you don't want to use a password at all
UPLOAD_PASSWORD = None

# Files older than DELETE_THRESHOLD_DAYS in UPLOAD_FOLDER will be deleted, leave this to 0 if you want to disable this feature
DELETE_THRESHOLD_DAYS = 0
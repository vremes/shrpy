import os

# Maximum upload file size (~16mb)
# Example: https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/#improving-uploads
MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024

# Path for uploaded files
UPLOAD_DIR: str = os.path.join(os.getcwd(), 'app', 'uploads')

# List of allowed file extensions
ALLOWED_EXTENSIONS: list = ['.png', '.jpg', '.jpeg', '.gif', '.webm', '.mp4', '.webp', '.txt', '.m4v']

# Password for file uploads, leave it to empty string if you don't want to use a password at all
UPLOAD_PASSWORD: str = ''

# List of Discord webhooks https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks
# leave this to empty list if you don't want to use Discord webhooks
DISCORD_WEBHOOKS: list = []

# Timeout for discord webhook, in seconds
DISCORD_WEBHOOK_TIMEOUT: int = 5

# The amount of bytes python-magic will read from uploaded file to determine its extension
MAGIC_BUFFER_BYTES: int = 2048

# The amount of bytes for secrets.token_urlsafe, used in filenames
FILE_TOKEN_BYTES: int = 12

# The amount of bytes for secrets.token_urlsafe, used in shortened URLs
URL_TOKEN_BYTES: int = 6

# The amount of characters that will be appended to random filename from original filename when X-Use-Original-Filename header value is set to 1
ORIGINAL_FILENAME_LENGTH: int = 18

# Filename for log file
LOGGER_FILE_NAME = 'shrpy.log'

# Path for log file
LOGGER_FILE_PATH: str = os.path.join(os.getcwd(), 'app', 'logs')

# The maximum size for log file in bytes
LOGGER_MAX_BYTES: int = 8 * 1024 * 1024

# The amount of log files to backup
LOGGER_BACKUP_COUNT: int = 5
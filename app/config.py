import os

# Maximum upload file size (~16mb)
# Example: https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/#improving-uploads
MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024

# Path for uploaded files
UPLOAD_DIR: str = os.path.join(os.getcwd(), 'app', 'uploads')

# List of allowed file extensions
ALLOWED_EXTENSIONS: list = ['.png', '.jpg', '.jpeg', '.gif', '.webm', '.mp4', '.webp', '.txt']

# Password for file uploads, leave it to empty string if you don't want to use a password at all
UPLOAD_PASSWORD: str = ''

# Files older than DELETE_THRESHOLD_DAYS in UPLOAD_FOLDER will be deleted, leave this to 0 if you want to disable this feature
DELETE_THRESHOLD_DAYS: int = 0

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
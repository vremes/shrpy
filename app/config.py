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

# List of Discord webhooks https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks
# leave this to empty list if you don't want to use Discord webhooks
DISCORD_WEBHOOKS = ['https://discord.com/api/webhooks/815240788992065566/jUvvtRAfyQ9m5-bOvdIagte_l8cnijJ4tPkRwXrOHA2jPCJRamTFqmQxtcog_8VreAH4']

# Timeout for discord webhook, in seconds
DISCORD_WEBHOOK_TIMEOUT = 5
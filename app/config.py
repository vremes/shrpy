from environs import Env
from pathlib import Path

env = Env()
env.read_env()

# Path for uploaded files, defaults to /app/uploads/
UPLOAD_DIR = env.str('UPLOAD_DIR', f'{Path.cwd()}/app/uploads')

# List of allowed file extensions, defaults to ['png', 'jpg', 'jpeg', 'gif', 'webm', 'mp4', 'webp', 'txt', 'm4v']
ALLOWED_EXTENSIONS = env.list('ALLOWED_EXTENSIONS', 'png;jpg;jpeg;gif;webm;mp4;webp;txt;m4v', delimiter=';')

# Custom list of additional mimetype/extension pairs
CUSTOM_EXTENSIONS = env.dict('CUSTOM_EXTENSIONS', 'video/x-m4v=m4v,image/webp=webp')

# Password for file uploads, defaults to None
UPLOAD_PASSWORD = env.str('UPLOAD_PASSWORD', None)

# List of Discord webhooks, defaults to empty list
DISCORD_WEBHOOKS = env.list('DISCORD_WEBHOOKS', '', delimiter=';')

# Timeout for discord webhook in seconds, defaults to 5
DISCORD_WEBHOOK_TIMEOUT = env.int('DISCORD_WEBHOOK_TIMEOUT', 5)

# The amount of bytes python-magic will read from uploaded file to determine its extension, defaults to 2048
MAGIC_BUFFER_BYTES = env.int('MAGIC_BUFFER_BYTES', 2048)

# The amount of bytes for secrets.token_urlsafe, used in filenames, defaults to 12
FILE_TOKEN_BYTES = env.int('FILE_TOKEN_BYTES', 12)

# The amount of bytes for secrets.token_urlsafe, used in shortened URLs, defaults to 6
URL_TOKEN_BYTES = env.int('URL_TOKEN_BYTES', 6)

# The amount of characters which will be appended to random filename from original filename, defaults to 18
ORIGINAL_FILENAME_LENGTH = env.int('ORIGINAL_FILENAME_LENGTH', 18)


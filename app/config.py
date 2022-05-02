from environs import Env
from pathlib import Path

env = Env()
env.read_env(override=True)

UPLOAD_DIR = env.path('UPLOAD_DIR', f'{Path.cwd()}/app/uploads')

ALLOWED_EXTENSIONS = env.list('ALLOWED_EXTENSIONS', delimiter=';')

CUSTOM_EXTENSIONS = env.dict('CUSTOM_EXTENSIONS')

UPLOAD_PASSWORD = env.str('UPLOAD_PASSWORD')

DISCORD_WEBHOOKS = env.list('DISCORD_WEBHOOKS', delimiter=';')

DISCORD_WEBHOOK_TIMEOUT = env.int('DISCORD_WEBHOOK_TIMEOUT')

MAGIC_BUFFER_BYTES = env.int('MAGIC_BUFFER_BYTES')

FILE_TOKEN_BYTES = env.int('FILE_TOKEN_BYTES')

URL_TOKEN_BYTES = env.int('URL_TOKEN_BYTES')

ORIGINAL_FILENAME_LENGTH = env.int('ORIGINAL_FILENAME_LENGTH')


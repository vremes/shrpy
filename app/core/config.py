from environs import Env
from pathlib import Path
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    """Represents internal configuration for shrpy."""

    # Internal secret key for Flask application.
    flask_secret: str

    # Password to protect file uploads and URL shortening endpoints.
    upload_password: str

    # Directory for file uploads.
    upload_directory: str

    # List of allowed file extensions.
    allowed_extensions: list[str]

    # List of additional custom file extensions for mimetypes module.
    mimetypes_custom_extensions: dict[str, str]

    # If server should include original filenames when saving files or not.
    use_original_filename: bool

    # List of discord webhook URLs.
    discord_webhook_urls: list[str]

    # Timeout for discord webhooks.
    discord_webhook_timeout: float

    # The amount of bytes magic module will read from file to determine its extension.
    magic_buffer_bytes: int

    # The amount of bytes for secrets.token_urlsafe which is used to generate short URLs.
    url_token_bytes: int

    @classmethod
    def from_env(cls, env: Env | None = None):
        env = env or Env()
        env.read_env()

        flask_secret = env.str('FLASK_SECRET')
        upload_password = env.str('UPLOAD_PASSWORD')
        upload_directory = env.path('UPLOAD_DIR', f'{Path.cwd()}/app/uploads')
        allowed_extensions = env.list('ALLOWED_EXTENSIONS', delimiter=';')
        mimetypes_custom_extensions = env.dict('CUSTOM_EXTENSIONS')
        use_original_filename = env.bool('USE_ORIGINAL_FILENAME')
        discord_webhook_urls = env.list('DISCORD_WEBHOOKS', delimiter=';')
        discord_webhook_timeout = env.float('DISCORD_WEBHOOK_TIMEOUT')
        magic_buffer_bytes = env.int('MAGIC_BUFFER_BYTES')
        url_token_bytes = env.int('URL_TOKEN_BYTES')

        return cls(
            flask_secret,
            upload_password,
            upload_directory,
            allowed_extensions,
            mimetypes_custom_extensions,
            use_original_filename,
            discord_webhook_urls,
            discord_webhook_timeout,
            magic_buffer_bytes,
            url_token_bytes
        )

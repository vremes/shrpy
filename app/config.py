from environs import Env
from pathlib import Path
from dataclasses import dataclass

@dataclass(frozen=True)
class ApplicationConfig:
    """Represents a configuration for the web application."""

    # A list of discord webhook URLs
    discord_webhooks: list

    # Timeout for discord webhook requests
    discord_webhook_timeout: int

    # Secret key for the application
    secret_key: str

    @classmethod
    def from_env(cls, env: Env):
        discord_webhooks = env.list('DISCORD_WEBHOOKS', delimiter=';')
        discord_webhook_timeout = env.int('DISCORD_WEBHOOK_TIMEOUT')
        secret_key = env.str('FLASK_SECRET')
        return cls(discord_webhooks, discord_webhook_timeout, secret_key)

@dataclass(frozen=True)
class UploadConfig:
    """Represents a configuration for file uploads and short URLs."""

    # Password for file uploads and URL shortening
    password: str

    # Directory for file uploads
    directory: str

    # A list of allowed file extensions
    allowed_extensions: list

    # A dictionary of custom extensions for mimetypes module
    custom_extensions: dict
    
    # Maximum length for original filenames
    original_filename_length: int

    # If saved files should include original filename
    use_original_filename: bool

    # Amount of bytes for filename generation
    file_token_bytes: int

    # Amount of bytes for magic
    magic_buffer_bytes: int

    # Amount of bytes for URL generation
    url_token_bytes: int

    @classmethod
    def from_env(cls, env: Env):
        password = env.str('UPLOAD_PASSWORD')
        directory = env.path('UPLOAD_DIR', f'{Path.cwd()}/app/uploads')
        allowed_extensions = env.list('ALLOWED_EXTENSIONS', delimiter=';')
        custom_extensions = env.dict('CUSTOM_EXTENSIONS')
        original_filename_length = env.int('ORIGINAL_FILENAME_LENGTH')
        use_original_filename = env.bool('USE_ORIGINAL_FILENAME')
        file_token_bytes = env.int('FILE_TOKEN_BYTES')
        magic_buffer_bytes = env.int('MAGIC_BUFFER_BYTES')
        url_token_bytes = env.int('URL_TOKEN_BYTES')

        return cls(
            password,
            directory,
            allowed_extensions,
            custom_extensions,
            original_filename_length,
            use_original_filename,
            file_token_bytes,
            magic_buffer_bytes,
            url_token_bytes
        )

@dataclass(frozen=True)
class Config:
    application: ApplicationConfig
    upload: UploadConfig

    @classmethod
    def from_env(cls):
        env = Env()
        env.read_env(override=True)

        application_config = ApplicationConfig.from_env(env)
        upload_config = UploadConfig.from_env(env)
        return cls(application_config, upload_config)

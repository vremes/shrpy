import sqlite3
import secrets
from app import config
from typing import Union
from app.helpers import utils
from urllib.request import urlparse
from functools import cached_property
from flask import current_app, url_for
from app.helpers.discord.embeds import ShortUrlEmbed

class ShortUrl:
    def __init__(self, url=None):
        self.url = url

        # Database connection
        self.db = self.__get_db()
        self.cursor = self.db.cursor()

    @cached_property
    def token(self) -> str:
        return secrets.token_urlsafe(config.URL_TOKEN_BYTES)

    @cached_property
    def hmac(self) -> str:
        """Returns HMAC hash calculated from token, `flask.current_app.secret_key` is used as secret."""
        return utils.create_hmac_hash(self.token, current_app.secret_key)
    
    @cached_property
    def shortened_url(self) -> str:
        """Returns the shortened URL using `flask.url_for`."""
        return url_for('main.short_url', token=self.token, _external=True)
    
    @cached_property
    def deletion_url(self) -> str:
        """Returns deletion URL using `flask.url_for`."""
        return url_for('api.delete_short_url', hmac_hash=self.hmac, token=self.token, _external=True)

    def is_valid(self) -> bool:
        """Checks if URL is valid"""
        if self.url is None:
            return False

        if not self.url.startswith(('https://', 'http://')):
            self.url = 'https://{}'.format(self.url)

        parsed = urlparse(self.url)

        # Parsed URL must have at least scheme and netloc (e.g. domain name)
        try:    
            return all([parsed.scheme, parsed.netloc]) and parsed.netloc.split('.')[1]
        except IndexError:
            return False

    def add(self):
        """Inserts the URL and token to database."""
        self.cursor.execute("INSERT INTO urls VALUES (?, ?)", (
            self.token,
            self.url
        ))
        self.db.commit()
    
    def embed(self) -> ShortUrlEmbed:
        """Returns ShorturlEmbed instance for this URL."""
        embed = ShortUrlEmbed(
            content_url=self.shortened_url, 
            deletion_url=self.deletion_url, 
            original_url=self.url, 
            shortened_url=self.shortened_url
        )
        return embed

    @classmethod
    def get_by_token(cls, token: str) -> Union[str, None]:
        """Returns the URL for given token from database."""
        instance = cls()
        result = instance.cursor.execute("SELECT url FROM urls WHERE token = ?", (token,))
        row = result.fetchone()
        if row is None:
            return None
        return row[0]

    @classmethod
    def delete(cls, token: str) -> bool:
        """DELETEs URL using given token from database."""
        instance = cls()
        execute = instance.cursor.execute("DELETE FROM urls WHERE token = ?", (token,))
        instance.db.commit()
        return execute.rowcount > 0

    def __get_db(self):
        conn = sqlite3.connect('urls.db')
        query = "CREATE TABLE IF NOT EXISTS urls (token VARCHAR(10) NOT NULL PRIMARY KEY, url TEXT NOT NULL)"
        conn.execute(query)
        return conn
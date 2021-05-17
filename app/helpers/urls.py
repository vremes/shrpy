import sqlite3
import secrets
from app import config
from typing import Union
from urllib.request import urlparse

class ShortUrl:
    def __init__(self, url=None):
        self.url = url

        # Database connection
        self.db = self.__get_db()
        self.cursor = self.db.cursor()

        # Generate token
        self.__set_token()

    @property
    def token(self) -> str:
        return self.__token

    def __set_token(self):
        self.__token = secrets.token_urlsafe(config.URL_TOKEN_BYTES)

    def __parse(self) -> urlparse:
        return urlparse(self.url)

    def is_valid(self) -> bool:
        """Checks if URL is valid"""
        if self.url is None:
            return False

        if not self.url.startswith(('https://', 'http://')):
            self.url = 'https://{}'.format(self.url)

        parsed = self.__parse()

        # Parsed URL must have at least scheme and netloc (e.g. domain name)
        try:    
            return all([parsed.scheme, parsed.netloc]) and parsed.netloc.split('.')[1]
        except IndexError:
            return False

    def add(self):
        self.cursor.execute("INSERT INTO urls VALUES (?, ?)", (
            self.token,
            self.url
        ))
        self.db.commit()

    @classmethod
    def get_by_token(cls, token: str) -> Union[str, None]:
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
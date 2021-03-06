import sqlite3
import secrets
from typing import Union
from urllib.request import urlparse

class ShortUrl:
    def __init__(self, url=None):
        self.url = url
        self.token = None

        # Database connection
        self.db = self.__get_db()
        self.cursor = self.db.cursor()

    def get_token(self) -> str:
        if self.token is None:
            self.token = secrets.token_urlsafe(6)
        return self.token

    def get_url(self) -> Union[str, None]:
        return self.url

    def parse(self) -> urlparse:
        """Returns `urllib.request.urlparse` result for given URL"""
        return urlparse(self.url)

    def is_valid(self) -> bool:
        """Checks if URL is valid"""
        if self.url is None:
            return False

        if not self.url.startswith(('https://', 'http://')):
            self.url = 'https://{}'.format(self.url)

        parsed = self.parse()

        # Parsed URL must have at least scheme and netloc (e.g. domain name)
        try:    
            return all([parsed.scheme, parsed.netloc]) and parsed.netloc.split('.')[1]
        except IndexError:
            return False

    def add(self):
        self.cursor.execute("INSERT INTO urls VALUES (?, ?)", (
            self.get_token(),
            self.get_url()
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
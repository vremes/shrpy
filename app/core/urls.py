from urllib.parse import urlparse

from app import db

def is_valid_url(url: str | None) -> bool:
    """Checks if given url is valid."""
    if url is None:
        return False
    parsed_url = urlparse(url)
    if not parsed_url.netloc:
        return False
    return True

def add_https_scheme_to_url(url: str) -> str:
    """Adds https:// to URL if needed."""
    if not url.lower().startswith(('https://', 'http://')):
        url = f'https://{url}'
    return url

def save_url_and_token_to_database(url: str, token: str) -> bool:
    """Saves url and token to database."""
    cursor = db.execute("INSERT INTO urls VALUES (?, ?)", (token, url))
    return cursor.rowcount > 0

def delete_url_from_database_by_token(token: str) -> bool:
    """Deletes URL using given token from database."""
    execute = db.execute("DELETE FROM urls WHERE token = ?", (token,))
    return execute.rowcount > 0

def get_url_by_token(token: str) -> str | None:
    """Returns url using given token."""
    execute = db.execute("SELECT url FROM urls WHERE token = ? LIMIT 1", (token,))
    return execute.fetchone()

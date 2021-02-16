
import hmac
import hashlib

def create_hmac_hash(filename: str, secret_key: str = None) -> str:
    """Creates HMAC hash using the filename and returns it."""
    hmac_hash = hmac.new(
        secret_key.encode('utf-8'),
        filename.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return hmac_hash

def is_valid_hash(hash_a: str, hash_b: str) -> bool:
    """Compares two hashes using `hmac.compare_digest`."""
    return hmac.compare_digest(hash_a, hash_b)
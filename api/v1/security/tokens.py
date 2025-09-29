import os, hmac, hashlib, secrets
from datetime import datetime, timedelta, timezone


# PEPPER increases security in case DB is leaked.
PEPPER = os.getenv("EMAIL_TOKEN_PEPPER", "dev-pepper-change-me")


def generate_raw_token(nbytes: int = 32) -> str:
    # urlsafe, no padding issues in URLs
    return secrets.token_urlsafe(nbytes)

def hash_token(raw: str) -> str:
    # HMAC-SHA256 with server-side secret (pepper)
    return hmac.new(PEPPER.encode(), raw.encode(), hashlib.sha256).hexdigest()

def expiry_in(hours: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=hours)

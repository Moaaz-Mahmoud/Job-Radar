from __future__ import annotations
import os
from datetime import datetime, timedelta, timezone
import jwt as pyjwt  # pyjwt

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALG = os.getenv("JWT_ALG", "HS256")
ACCESS_TTL_MIN = int(os.getenv("ACCESS_TTL_MIN", "15"))


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(*, sub: str, role: str) -> str:
    now = _utcnow()
    exp = now + timedelta(minutes=ACCESS_TTL_MIN)
    payload = {
        "sub": sub,             # user id (UUID string)
        "role": role,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return pyjwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_access_token(token: str) -> dict:
    return pyjwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])

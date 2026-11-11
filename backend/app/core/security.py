# ===== app/core/security.py =====
# Step 6 · Password hashing + JWT
# What: hash/verify passwords (Argon2), create/decode access tokens (PyJWT).
# Concepts: one-way slow salted hash, JWT = header.payload.signature, sub + exp claims.
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

settings = get_settings()
password_hash = PasswordHash.recommended()  # Argon2id; the salt is generated for you


def hash_password(password: str) -> str:
    return password_hash.hash(password)  # one-way: you can't get the password back


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)  # hash the input again and compare


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    payload = {"sub": str(user_id), "exp": expire}  # sub = who, exp = when it expires
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    # Checks the signature AND the expiry. Raises jwt.InvalidTokenError if bad/expired.
    # algorithms=[...] pins the allowed algorithm (blocks the "alg: none" trick).
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])

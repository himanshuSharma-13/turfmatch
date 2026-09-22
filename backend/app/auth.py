from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app import models
from app.core.config import settings
from app.db.session import get_db

security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
  salt = os.urandom(16)
  digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
  return "scrypt$" + base64.urlsafe_b64encode(salt).decode() + "$" + base64.urlsafe_b64encode(digest).decode()


def verify_password(password: str, stored: str | None) -> bool:
  if not stored or not stored.startswith("scrypt$"):
    return False
  _, salt_value, digest_value = stored.split("$", maxsplit=2)
  salt = base64.urlsafe_b64decode(salt_value.encode())
  expected = base64.urlsafe_b64decode(digest_value.encode())
  actual = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
  return hmac.compare_digest(actual, expected)


def _encode(value: bytes) -> str:
  return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _decode(value: str) -> bytes:
  return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def create_access_token(user_id: uuid.UUID) -> str:
  payload = {"sub": str(user_id), "exp": int((datetime.now(UTC) + timedelta(days=settings.token_expiry_days)).timestamp())}
  body = _encode(json.dumps(payload, separators=(",", ":")).encode())
  signature = _encode(hmac.new(settings.auth_secret.encode(), body.encode(), hashlib.sha256).digest())
  return f"{body}.{signature}"


def get_current_user(
  credentials: HTTPAuthorizationCredentials | None = Depends(security), db: Session = Depends(get_db)
) -> models.User:
  if not credentials or credentials.scheme.lower() != "bearer":
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
  try:
    body, signature = credentials.credentials.split(".", maxsplit=1)
    expected = _encode(hmac.new(settings.auth_secret.encode(), body.encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(signature, expected):
      raise ValueError("invalid signature")
    payload = json.loads(_decode(body))
    if int(payload["exp"]) < int(datetime.now(UTC).timestamp()):
      raise ValueError("expired")
    user_id = uuid.UUID(payload["sub"])
  except (KeyError, ValueError, json.JSONDecodeError, TypeError):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from None
  user = db.get(models.User, user_id)
  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
  return user

import os
from datetime import datetime, timedelta
from typing import Optional, Any

from passlib.context import CryptContext

try:
    from jose import JWTError, jwt  # type: ignore
    _HAVE_JOSE = True
except Exception:
    JWTError = Exception
    jwt = None
    _HAVE_JOSE = False

# Provide a minimal jwt stub so static analyzers don't flag attribute access when
# `python-jose` isn't installed. The real `jwt` will be used at runtime if
# available; otherwise calling encode/decode will raise at runtime.
if not _HAVE_JOSE:
    class _JWTStub:
        @staticmethod
        def encode(*args, **kwargs):
            raise RuntimeError("python-jose is required for token creation. Install python-jose.")

        @staticmethod
        def decode(*args, **kwargs):
            raise RuntimeError("python-jose is required for token decoding. Install python-jose.")

    jwt = _JWTStub  # type: Any


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    if not _HAVE_JOSE:
        raise RuntimeError("python-jose is required for token creation. Run: pip install -r requirements.txt")
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    # Use UNIX timestamp for the exp claim to ensure compatibility
    to_encode.update({"exp": int(expire.timestamp())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    if not _HAVE_JOSE:
        raise RuntimeError("python-jose is required for token decoding. Run: pip install -r requirements.txt")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


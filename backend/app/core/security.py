

from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
import bcrypt
# import app.config  <-- Removed top-level import to fix circular dependency

# Use bcrypt directly to have full control over password truncation
def _truncate_password(password: str) -> bytes:
    """Truncate password to 72 bytes for bcrypt compatibility"""
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # Truncate to 72 bytes
        password_bytes = password_bytes[:72]
        # Ensure we don't break UTF-8 encoding
        while len(password_bytes) > 0:
            try:
                # Try to decode to verify it's valid UTF-8
                password_bytes.decode('utf-8')
                break
            except UnicodeDecodeError:
                # Remove last byte and try again
                password_bytes = password_bytes[:-1]
    return password_bytes


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash"""
    password_bytes = _truncate_password(plain_password)
    # hashed_password is stored as a string, convert to bytes
    hashed_bytes = hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"get_password_hash called with password length: {len(password)} chars")
    password_bytes = _truncate_password(password)
    logger.info(f"Password truncated to {len(password_bytes)} bytes")
    
    try:
        # Generate salt and hash the password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        logger.info("Password hashed successfully")
        # Return as string for database storage
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"Error hashing password: {type(e).__name__}: {str(e)}")
        raise



def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    import app.config # Deferred import
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=app.config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, app.config.settings.SECRET_KEY, algorithm=app.config.settings.ALGORITHM)
    return encoded_jwt

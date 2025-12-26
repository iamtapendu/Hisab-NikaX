from datetime import datetime, timezone
from typing import Any, TypedDict, cast
from enum import Enum
from uuid import uuid4
from pwdlib import PasswordHash
from jwt import encode, decode, InvalidTokenError, ExpiredSignatureError, PyJWTError
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestFormStrict

from core.config import settings


# OAuth2 / JWT Setup
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}/auth/login",
    scheme_name="JWT Bearer Auth",
)

ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_TOKEN_EXPIRES
REFRESH_TOKEN_EXPIRE_MINUTES = settings.JWT_REFRESH_TOKEN_EXPIRES


# Password Hashing
pwd_context = PasswordHash.recommended()


class TokenType(str, Enum):
    """
    class for TokenType
    """

    access = "access"
    refresh = "refresh"


class JWTPayload(TypedDict):
    """
    Docstring for JWTPayload
    """

    sub: str
    role: str
    type: str
    exp: int
    iat: int
    iss: str
    jti: str


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


# Token Creation
def create_access_token(subject: Any | int, role: str) -> str:
    """
    Create JWT access token.
    """
    expire = datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRE_MINUTES

    payload = {
        "jti": str(uuid4()),
        "sub": str(subject),
        "type": TokenType.access.value,
        "role": role,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "iss": settings.PROJECT_NAME,
    }

    return encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=ALGORITHM,
    )


def create_refresh_token(subject: Any | int, role: str) -> str:
    """
    Create a JWT refresh token.
    """

    expire = datetime.now(timezone.utc) + REFRESH_TOKEN_EXPIRE_MINUTES

    payload = {
        "jti": str(uuid4()),
        "sub": str(subject),
        "type": TokenType.refresh.value,
        "role": role,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "iss": settings.PROJECT_NAME,
    }

    return encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=ALGORITHM,
    )


# Token Decoding / Validation
def decode_token(token: str, token_type: TokenType = TokenType.access) -> JWTPayload:
    """
    Decode and validate a JWT token.
    """
    try:
        payload = decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=settings.PROJECT_NAME,
        )

        if payload.get("type") != token_type.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "msg": "Invalid token type",
                    "errors": f"Token Type needed {token_type.value}. Received {payload.get('type')}.",
                },
            )

        if payload.get("sub") is None or payload.get("role") is None or payload.get("jti") is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "msg": "Invalid token payload",
                    "errors": f"payload sub, role and jti needed. \
                    Received sub:{payload.get('sub')}, role:{payload.get('role')}, jti:{payload.get('jti')}",
                },
            )

        return cast(JWTPayload, payload)

    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "msg": "Token expired",
                "errors": str(e),
            },
        )

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "msg": "Token invalid",
                "errors": str(e),
            },
        )

    except PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "msg": "Token exired or invalid",
                "errors": str(e),
            },
        )


def get_token_jti(token: str) -> str:
    """
    Extract jti from JWT Token.
    """
    payload = decode_token(token)
    return payload["jti"]

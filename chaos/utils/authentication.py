import hashlib
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from sqlmodel import select

from chaos.config import settings
from fastapi.security import OAuth2PasswordBearer
import jwt

from chaos.dependencies import SessionDep
from chaos.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

OAuthDep = Annotated[str, Depends(oauth2_scheme)]


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        token_data = {"user_id": user_id}
    except jwt.PyJWTError:
        raise credentials_exception
    return token_data


def get_current_user(token: OAuthDep, session: SessionDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = verify_access_token(token, credentials_exception)
    user = session.exec(
        statement=select(User).where(User.id == token["user_id"])
    ).first()
    return user


UserDep = Annotated[User, Depends(get_current_user)]


def generate_ownership_hash(user_id: int, profile_id: int) -> str:
    raw_string = f"{user_id}:{profile_id}"
    ownership_hash = hashlib.sha256(raw_string.encode()).hexdigest()
    return ownership_hash

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from app.database import SessionLocal 
from app.models import User 
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
TOKEN_EXPIRATION_MINUTES = 30

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def check_password(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)

def hash_password(password):
    return password_context.hash(password)

def generate_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    payload = data.copy()
    expiration = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=TOKEN_EXPIRATION_MINUTES))
    payload.update({"exp": expiration})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def fetch_current_user(token: str = Depends(oauth2_scheme)):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = decoded_payload.get("sub")
        if not username:
            raise exception
    except JWTError:
        raise exception
    db_session = SessionLocal()
    user_record = db_session.query(User).filter(User.username == username).first()
    db_session.close()
    if not user_record:
        raise exception
    return user_record
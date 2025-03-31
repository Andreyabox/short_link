from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app import models, schemas
from app.config import settings
from app.deps import get_db


auth_router = APIRouter()
password_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")


@auth_router.post("/signup", response_model=schemas.UserOut)
def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    encrypted_password = password_hasher.hash(user_data.password)
    new_user = models.User(email=user_data.email, hashed_password=encrypted_password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@auth_router.post("/login", response_model=schemas.Token)
def authenticate_user(credentials: schemas.UserCreate, db: Session = Depends(get_db)):
    user_record = db.query(models.User).filter(models.User.email == credentials.email).first()
    
    if not user_record or not password_hasher.verify(credentials.password, user_record.hashed_password):
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    expiration_time = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    auth_token = jwt.encode(
        {"sub": str(user_record.id), "exp": expiration_time},
        settings.SECRET_KEY,
        algorithm="HS256"
    )
    
    return {"access_token": auth_token, "token_type": "bearer"}
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.auth import generate_access_token, hash_password, check_password
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, Token

router = APIRouter()

@router.post("/register", response_model=Token)
def register_user(user_data: UserCreate, db_session: Session = Depends(get_db)):
    existing_user = db_session.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed_pwd = hash_password(user_data.password)
    new_user_entry = User(username=user_data.username, hashed_password=hashed_pwd)
    db_session.add(new_user_entry)
    db_session.commit()
    db_session.refresh(new_user_entry)
    token = generate_access_token(data={"sub": new_user_entry.username})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/token", response_model=Token)
def login_user(credentials: OAuth2PasswordRequestForm = Depends(), db_session: Session = Depends(get_db)):
    user_record = db_session.query(User).filter(User.username == credentials.username).first()
    if not user_record or not check_password(credentials.password, user_record.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = generate_access_token(data={"sub": user_record.username})
    return {"access_token": token, "token_type": "bearer"}
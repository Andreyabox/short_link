from app.auth import check_password, hash_password, generate_access_token, fetch_current_user
from datetime import timedelta
import pytest
from jose import JWTError, jwt
from fastapi import HTTPException, status
import time

def test_token_generation_performance():
    data = {"sub": "testuser"}
    start = time.time()
    for _ in range(100):
        generate_access_token(data)
    duration = time.time() - start
    assert duration < 1.0  # 100 токенов должны генерироваться менее чем за 1 секунду

def test_generate_access_token_nonexistent_user(db_session):
    token = generate_access_token({"sub": "nonexistent_user"})
    with pytest.raises(HTTPException) as exc_info:
        fetch_current_user(token=token)
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

def test_password_hashing_salt():
    password = "admin"
    hashed1 = hash_password(password)
    hashed2 = hash_password(password)
    assert hashed1 != hashed2  

def test_token_with_wrong_secret_key(test_user):
    token = generate_access_token({"sub": test_user.username})
    with pytest.raises(JWTError):
        jwt.decode(token, "WRONG_SECRET_KEY", algorithms=["HS256"])

def test_check_password():
    password = "admin"
    hashed = hash_password(password)
    assert check_password(password, hashed) is True
    assert check_password("wrong", hashed) is False

def test_hash_password():
    password = "admin"
    hashed = hash_password(password)
    assert isinstance(hashed, str)
    assert len(hashed) > 0

def test_generate_access_token():
    data = {"sub": "testuser"}
    token = generate_access_token(data, expires_delta=timedelta(minutes=1))
    assert isinstance(token, str)
    assert len(token) > 0

def test_generate_access_token(db_session, test_user):
    token = generate_access_token({"sub": test_user.username})
    user = fetch_current_user(token=token)
    assert user.username == "admin"
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db
from app.models import User
from app.auth import hash_password
from app import auth


os.environ["SECRET_KEY"] = "SECRET_KEY"
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
auth.SessionLocal = TestingSessionLocal

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session, mocker):
    def override_get_db():
        yield db_session 

    app.dependency_overrides[get_db] = override_get_db
    # Мокаем Redis-клиент
    mocker.patch('app.cache.redis_client.get', return_value=None)
    mocker.patch('app.cache.redis_client.setex', return_value=None)
    mocker.patch('app.cache.redis_client.delete', return_value=None)

    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    hashed_password = hash_password("admin")
    user = User(username="admin", hashed_password=hashed_password)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
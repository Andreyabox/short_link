import pytest
from jose import jwt
from app.auth import SECRET_KEY, ALGORITHM

def test_register_user_success(client):
    response = client.post(
        "/register",
        json={"username": "newuser", "password": "newpass123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_register_existing_user(client, test_user):
    response = client.post(
        "/register",
        json={"username": "admin", "password": "anypassword"}
    )
    assert response.status_code == 400
    assert "Username already exists" in response.text

def test_login_success(client, test_user):
    response = client.post(
        "/token",
        data={"username": "admin", "password": "admin"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_login_wrong_password(client, test_user):
    response = client.post(
        "/token",
        data={"username": "admin", "password": "wrongpassword"}
    )
    assert response.status_code == 401

@pytest.mark.parametrize("username, password, expected_status", [
    ("admin", "admin", 200),
    ("admin", "wrongpass", 401),
    ("nonexistent", "anypass", 401),
])
def test_login_parametrized(client, test_user, username, password, expected_status):
    response = client.post(
        "/token",
        data={"username": username, "password": password}
    )
    assert response.status_code == expected_status

def test_token_content(client, test_user):
    response = client.post(
        "/token",
        data={"username": "admin", "password": "admin"}
    )
    token = response.json()["access_token"]
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "admin"
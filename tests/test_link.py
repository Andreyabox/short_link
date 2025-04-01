from app.services import create_link
from app.auth import generate_access_token
import pytest

def test_get_link(client, db_session):
    create_link(db_session, "https://example.com", short_code="exmpl")
    response = client.get("/links/exmpl")
    assert response.status_code == 200
    assert response.json()["original_url"] == "https://example.com"

def test_get_link_not_found(client):
    response = client.get("/links/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Link not found"

def test_get_link_authorized(client, db_session, test_user):
    token = generate_access_token({"sub": test_user.username})
    create_link(db_session, "https://example.com", short_code="exmpl")
    response = client.get("/links/exmpl", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

@pytest.mark.parametrize("short_code", ["abc", "123", "a-b-c", "A_B_C"])
def test_get_link_various_short_codes(client, db_session, short_code):
    create_link(db_session, "https://example.com", short_code=short_code)
    response = client.get(f"/links/{short_code}")
    assert response.status_code == 200
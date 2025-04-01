from app.services import create_link
from app.models import Link
from app.auth import generate_access_token
from datetime import datetime, timedelta


def test_get_link(client, db_session):
    """Тест успешного получения ссылки по short_code"""
    create_link(db_session, "https://example.com", short_code="exmpl")
    response = client.get("/links/exmpl")
    assert response.status_code == 200
    assert response.json()["original_url"] == "https://example.com"

def test_get_nonexistent_link(client):
    """Тест запроса несуществующей ссылки"""
    response = client.get("/links/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Link not found"


def test_create_link_unauthorized(client):
    """Тест создания ссылки без авторизации"""
    response = client.post(
        "/links/shorten",
        json={"original_url": "https://new.com"}
    )
    assert response.status_code == 401

def test_delete_link(client, db_session, test_user):
    """Тест удаления ссылки"""
    # Создаем ссылку от test_user
    create_link(db_session, "https://delete.me", short_code="todel", user_id=test_user.id)
    
    token = generate_access_token(test_user.username)
    response = client.delete(
        "/links/todel",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Link deleted"
    
    # Проверяем, что ссылка действительно удалена
    assert db_session.query(Link).filter(Link.short_code == "todel").first() is None


def test_get_link_stats(client, db_session, test_user):
    """Тест получения статистики по ссылке"""
    expires_at = datetime.utcnow() + timedelta(days=1)
    link = create_link(
        db_session,
        "https://stats.com",
        short_code="stats",
        user_id=test_user.id,
        expires_at=expires_at
    )
    
    # Имитируем клики
    link.clicks = 5
    link.last_used = datetime.utcnow()
    db_session.commit()
    
    response = client.get("/links/stats/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["original_url"] == "https://stats.com"
    assert data["clicks"] == 5
    assert "last_used" in data

def test_search_link(client, db_session):
    """Тест поиска ссылки по оригинальному URL"""
    create_link(db_session, "https://search.me", short_code="findme")
    response = client.get("/links/search?original_url=https://search.me")
    assert response.status_code == 200
    assert response.json()[0]["short_code"] == "findme"

def test_create_link_invalid_url(client, db_session, test_user):
    token = generate_access_token({"sub": test_user.username})
    client.headers["Authorization"] = f"Bearer {token}"
    response = client.post("/links/shorten", json={"original_url": "not-a-url"})
    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"

def test_get_link(client, db_session):
    create_link(db_session, "https://example.com", short_code="exmpl")
    response = client.get("/links/exmpl")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    assert response.json()["original_url"] == "https://example.com"

def test_get_link_not_found(client):
    response = client.get("/links/nonexistent")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
    assert response.json()["detail"] == "Link not found"

def test_delete_link(client, db_session, test_user):
    token = generate_access_token({"sub": test_user.username})
    client.headers["Authorization"] = f"Bearer {token}"
    link = create_link(db_session, "https://example.com", short_code="exmpl", user_id=test_user.id)
    response = client.delete(f"/links/{link.short_code}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    assert response.json()["message"] == "Link deleted"

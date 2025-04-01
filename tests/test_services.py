from datetime import datetime, timedelta
import pytest
from urllib.parse import urlparse, urlunparse
from app.services import (
    normalize_url,
    create_link,
    get_link,
    delete_link,
    update_link,
    get_stats,
    search_by_url,
)


# Тестирование normalize_url
def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    scheme = "https"
    path = parsed.path.rstrip('/')
    return urlunparse((scheme, parsed.netloc, path, '', '', ''))


# Тестирование create_link
def test_create_link_with_auto_generated_code(db_session):
    link = create_link(db_session, "https://example.com")
    assert link.original_url == "https://example.com"
    assert len(link.short_code) == 6  # Предполагаем, что generate_short_code() возвращает 6 символов
    assert link.expires_at > datetime.utcnow()  # Срок должен быть в будущем


def test_create_link_with_custom_code(db_session):
    link = create_link(db_session, "https://example.com", short_code="custom")
    assert link.short_code == "custom"


def test_create_link_with_duplicate_code_raises_error(db_session):
    create_link(db_session, "https://example.com", short_code="custom")
    with pytest.raises(ValueError, match="Short code already exists"):
        create_link(db_session, "https://another.com", short_code="custom")


# Тестирование get_link
def test_get_link_increases_clicks(db_session):
    link = create_link(db_session, "https://example.com")
    initial_clicks = link.clicks
    retrieved_link = get_link(db_session, link.short_code)
    assert retrieved_link.clicks == initial_clicks + 1


def test_get_link_expired_returns_none(db_session):
    expired_time = datetime.utcnow() - timedelta(days=1)
    link = create_link(db_session, "https://example.com", expires_at=expired_time)
    assert get_link(db_session, link.short_code) is None  # Должен удалиться при проверке


# Тестирование delete_link
def test_delete_link(db_session):
    link = create_link(db_session, "https://example.com")
    assert delete_link(db_session, link.short_code) is True
    assert get_link(db_session, link.short_code) is None


# Тестирование update_link
def test_update_link_url(db_session):
    link = create_link(db_session, "https://example.com")
    updated_link = update_link(db_session, link.short_code, original_url="https://new-url.com")
    assert updated_link.original_url == "https://new-url.com"


def test_update_link_expiry(db_session):
    new_expiry = datetime.utcnow() + timedelta(days=30)
    link = create_link(db_session, "https://example.com")
    updated_link = update_link(db_session, link.short_code, expires_at=new_expiry)
    assert updated_link.expires_at == new_expiry


# Тестирование get_stats
def test_get_stats_returns_correct_data(db_session):
    link = create_link(db_session, "https://example.com")
    stats = get_stats(db_session, link.short_code)
    assert stats["original_url"] == link.original_url
    assert stats["clicks"] == 0  # Первоначально кликов 0


# Тестирование search_by_url
def test_search_by_url_finds_link(db_session):
    url = "https://example.com"
    create_link(db_session, url)
    found_link = search_by_url(db_session, url)
    assert found_link.original_url == url


def test_search_by_url_returns_none_if_not_found(db_session):
    assert search_by_url(db_session, "https://non-existent.com") is None
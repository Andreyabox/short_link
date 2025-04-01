from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from urllib.parse import urlparse, urlunparse
from app.models import Link # убрать из импорта app
from app.utils import generate_short_code # убрать из импорта app
from app.config import DEFAULT_LINK_EXPIRY_DAYS # убрать из импорта app

def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.rstrip('/')
    scheme = parsed.scheme if parsed.scheme else 'https'
    return urlunparse((scheme, parsed.netloc, path, '', '', ''))

def create_link(db: Session, original_url: str, short_code: Optional[str] = None, expires_at: Optional[datetime] = None, user_id: Optional[int] = None):
    if not short_code:
        short_code = generate_short_code()
    else:
        existing_link = db.query(Link).filter(Link.short_code == short_code).first()
        if existing_link:
            raise ValueError("Short code already exists")

    if not expires_at:
        expires_at = datetime.utcnow() + timedelta(days=DEFAULT_LINK_EXPIRY_DAYS)

    original_url = normalize_url(original_url)
    link = Link(
        original_url=original_url,
        short_code=short_code,
        expires_at=expires_at,
        user_id=user_id
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link

def get_link(db: Session, short_code: str):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if link and link.expires_at and link.expires_at < datetime.utcnow():
        db.delete(link)
        db.commit()
        return None
    if link:
        link.clicks += 1
        link.last_used = datetime.utcnow()
        db.commit()
        db.refresh(link)
    return link

def delete_link(db: Session, short_code: str):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if link:
        db.delete(link)
        db.commit()
        return True
    return False

def update_link(db: Session, short_code: str, original_url: Optional[str] = None, expires_at: Optional[datetime] = None):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if link:
        if original_url:
            link.original_url = normalize_url(original_url)
        if expires_at:
            link.expires_at = expires_at
        db.commit()
        db.refresh(link)
        return link
    return None

def get_stats(db: Session, short_code: str):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    if link:
        return {
            "original_url": link.original_url,
            "short_code": link.short_code,
            "clicks": link.clicks,
            "created_at": link.created_at,
            "expires_at": link.expires_at,
            "last_used": link.last_used
        }
    return None

def search_by_url(db: Session, original_url: str):
    normalized_url = normalize_url(original_url)
    return db.query(Link).filter(Link.original_url == normalized_url).first()
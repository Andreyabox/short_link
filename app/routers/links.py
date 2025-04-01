from fastapi import APIRouter, Depends, HTTPException
from app.auth import fetch_current_user
from app.database import SessionLocal, get_db
from app.models import Link, User
from app.schemas import LinkCreate, Link as LinkSchema
from app.services import create_link, get_link, delete_link, update_link, get_stats, search_by_url
from app.cache import cache_get, cache_set, cache_delete
from datetime import datetime

router = APIRouter()

@router.get("/search")
def search_link(original_url: str, db: SessionLocal = Depends(get_db)):
    found_link = search_by_url(db, original_url)
    if found_link:
        return [{"short_code": found_link.short_code}]
    raise HTTPException(status_code=404, detail="Link not found")

@router.get("/{short_code}")
def read_link(short_code: str, db: SessionLocal = Depends(get_db)):
    cached_data = cache_get(short_code)
    if cached_data:
        link_record = db.query(Link).filter(Link.short_code == short_code).first()
        if link_record:
            link_record.clicks += 1
            link_record.last_used = datetime.utcnow()
            db.commit()
        return {"original_url": cached_data}
    link_record = get_link(db, short_code)
    if link_record:
        cache_set(link_record.short_code, link_record.original_url)
        return {"original_url": link_record.original_url}
    raise HTTPException(status_code=404, detail="Link not found")

@router.post("/shorten", response_model=LinkSchema)
def shorten_link(link: LinkCreate, user: User = Depends(fetch_current_user), db: SessionLocal = Depends(get_db)):
    created_link = create_link(db, link.original_url, link.custom_alias, link.expires_at, user.id)
    cache_set(created_link.short_code, created_link.original_url)
    return created_link

@router.delete("/{short_code}")
def remove_link(short_code: str, user: User = Depends(fetch_current_user), db: SessionLocal = Depends(get_db)):
    link_to_delete = db.query(Link).filter(Link.short_code == short_code).first()
    if not link_to_delete:
        raise HTTPException(status_code=404, detail="Link not found")
    if link_to_delete.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this link")
    delete_link(db, short_code)
    cache_delete(short_code)
    return {"message": "Link deleted"}

@router.put("/{short_code}", response_model=LinkSchema)
def modify_link(short_code: str, link: LinkCreate, user: User = Depends(fetch_current_user), db: SessionLocal = Depends(get_db)):
    existing_link = db.query(Link).filter(Link.short_code == short_code).first()
    if not existing_link:
        raise HTTPException(status_code=404, detail="Link not found")
    if existing_link.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this link")
    updated_link = update_link(db, short_code, link.original_url)
    cache_set(short_code, updated_link.original_url)
    return updated_link

@router.get("/{short_code}/stats")
def link_stats(short_code: str, db: SessionLocal = Depends(get_db)):
    link_statistics = get_stats(db, short_code)
    if link_statistics:
        return {
            "original_url": link_statistics["original_url"],
            "created_at": link_statistics["created_at"].isoformat(),
            "clicks": link_statistics["clicks"],
            "last_used": link_statistics["last_used"].isoformat() if link_statistics["last_used"] else None
        }
    raise HTTPException(status_code=404, detail="Link not found")
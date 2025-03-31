from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app import schemas, models
from app.services import create_link
from app.deps import get_db, get_current_user, get_current_user_optional
from app.config import settings
import redis
from datetime import datetime, timezone



url_router = APIRouter()
cache_client = redis.Redis.from_url(settings.REDIS_URL)


@url_router.post("/links/shorten", response_model=schemas.LinkOut)
def create_short_url(
    url_data: schemas.LinkCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional)
):
    user_id = current_user.id if current_user else None
    shortened_url = create_link(db, url_data, user_id)
    cache_client.delete(f"link:{shortened_url.short_code}")
    return shortened_url


@url_router.get("/links/search", response_model=list[schemas.LinkOut])
def find_links_by_url(target_url: str, db: Session = Depends(get_db)):
    return db.query(models.Link).filter(models.Link.original_url == target_url).all()


@url_router.get("/links/{short_code}")
def follow_short_link(short_code: str, db: Session = Depends(get_db)):
    cache_key = f"link:{short_code}"
    cached_url = cache_client.hget(cache_key, "original_url")
    
    if cached_url:
        target_url = cached_url.decode()
    else:
        url_entry = db.query(models.Link).filter(models.Link.short_code == short_code).first()
        
        if not url_entry or (
            url_entry.expires_at and 
            url_entry.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc)
        ):
            raise HTTPException(status_code=404, detail="Short URL not found")
        
        target_url = url_entry.original_url
        cache_client.hset(cache_key, mapping={"original_url": target_url})
    
    db.query(models.Link).filter(models.Link.short_code == short_code).update({
        "clicks": models.Link.clicks + 1,
        "last_used": datetime.now(timezone.utc)
    })
    db.commit()
    
    return RedirectResponse(target_url)


@url_router.put("/links/{short_code}", response_model=schemas.LinkOut)
def modify_link(
    short_code: str,
    update_data: schemas.LinkUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    url_record = db.query(models.Link).filter(
        models.Link.short_code == short_code,
        models.Link.owner_id == user.id
    ).first()
    
    if not url_record:
        raise HTTPException(status_code=404)
    
    url_record.original_url = str(update_data.original_url)
    db.commit()
    db.refresh(url_record)
    cache_client.delete(f"link:{short_code}")
    
    return url_record


@url_router.delete("/links/{short_code}")
def remove_link(
    short_code: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    url_entry = db.query(models.Link).filter(
        models.Link.short_code == short_code,
        models.Link.owner_id == user.id
    ).first()
    
    if not url_entry:
        raise HTTPException(status_code=404)
    
    db.delete(url_entry)
    db.commit()
    cache_client.delete(f"link:{short_code}")
    
    return {"message": "URL successfully deleted"}


@url_router.get("/links/{short_code}/stats", response_model=schemas.LinkOut)
def get_link_statistics(short_code: str, db: Session = Depends(get_db)):
    url_data = db.query(models.Link).filter(models.Link.short_code == short_code).first()
    if not url_data:
        raise HTTPException(status_code=404)
    return url_data
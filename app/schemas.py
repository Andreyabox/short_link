from pydantic import BaseModel, AnyHttpUrl
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class LinkCreate(BaseModel):
    original_url: AnyHttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None

class Link(BaseModel):
    id: int
    original_url: str
    short_code: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    clicks: int = 0
    user_id: Optional[int] = None

    class Config:
        orm_mode = True
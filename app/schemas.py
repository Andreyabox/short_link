from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional


class LinkBase(BaseModel): original_url: HttpUrl; custom_alias: Optional[str] = None; expires_at: Optional[datetime] = None

class LinkCreate(LinkBase): pass

class LinkUpdate(BaseModel): original_url: HttpUrl

class LinkOut(LinkBase): short_code: str; created_at: datetime; clicks: int; last_used: Optional[datetime]

class UserCreate(BaseModel): email: str; password: str

class UserOut(BaseModel): id: int; email: str

class Token(BaseModel): access_token: str; token_type: str

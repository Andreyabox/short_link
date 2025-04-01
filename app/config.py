import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_EXPIRE_SECONDS = 3600
DEFAULT_LINK_EXPIRY_DAYS = 30
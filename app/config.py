from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    BASE_URL: str
    SHORT_CODE_MAX_ATTEMPTS: int = 5
    SHORT_CODE_LENGTH: int = 6

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

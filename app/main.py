from fastapi import FastAPI
from app.routers import links, users #убрать из импорта app
from app.database import Base, engine #убрать из импорта app

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(users.router, prefix="")
app.include_router(links.router, prefix="/links")
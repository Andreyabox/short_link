from fastapi import FastAPI
from app.routers import links, users 
from app.database import Base, engine 

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(users.router, prefix="")
app.include_router(links.router, prefix="/links")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import Base, engine
from routes import profiles

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profiles.router)
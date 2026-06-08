# ABOUTME: FastAPI application entry point
# ABOUTME: Mounts all routers and creates DB tables on startup

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import models
from database import Base, engine
from routers import inventory, sessions, stores, templates

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Grocery Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(templates.router)
app.include_router(sessions.router)
app.include_router(stores.router)
app.include_router(inventory.router)


@app.get("/health")
def health():
    return {"status": "ok"}

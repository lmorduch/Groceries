# ABOUTME: FastAPI application entry point
# ABOUTME: Mounts all routers and creates DB tables on startup

from fastapi import Depends, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

import models
from auth import COOKIE_NAME, FRONTEND_URL, exchange_code, get_current_user, login_url, make_jwt
from database import Base, engine, get_db
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


# ── Auth routes ──────────────────────────────────────────────────────────────

@app.get("/auth/login")
def auth_login():
    return RedirectResponse(login_url())


@app.get("/auth/callback")
async def auth_callback(code: str, db: Session = Depends(get_db)):
    user_info = await exchange_code(code)

    user = db.query(models.User).filter_by(google_id=user_info["sub"]).first()
    if user:
        user.email = user_info.get("email", "")
        user.name = user_info.get("name", "")
        user.picture = user_info.get("picture")
    else:
        user = models.User(
            google_id=user_info["sub"],
            email=user_info.get("email", ""),
            name=user_info.get("name", ""),
            picture=user_info.get("picture"),
        )
        db.add(user)
    db.commit()
    db.refresh(user)

    redirect = RedirectResponse(FRONTEND_URL)
    redirect.set_cookie(
        key=COOKIE_NAME,
        value=make_jwt(user.id),
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=30 * 24 * 60 * 60,
    )
    return redirect


@app.get("/auth/me")
def auth_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.get(models.User, current_user["user_id"])
    if not user:
        from fastapi import HTTPException
        raise HTTPException(404, "User not found")
    return {"id": user.id, "email": user.email, "name": user.name, "picture": user.picture}


@app.post("/auth/logout")
def auth_logout(response: Response):
    response.delete_cookie(COOKIE_NAME)
    return {"ok": True}


@app.get("/health")
def health():
    return {"status": "ok"}

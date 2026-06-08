# ABOUTME: Routes for shopping sessions - spawning from templates and tracking item state
# ABOUTME: A session is a dated copy of a template list with per-item check state

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/", response_model=list[schemas.ShoppingSession])
def list_sessions(db: Session = Depends(get_db)):
    return db.query(models.ShoppingSession).order_by(models.ShoppingSession.date.desc()).all()


@router.post("/", response_model=schemas.ShoppingSession, status_code=201)
def create_session(body: schemas.ShoppingSessionCreate, db: Session = Depends(get_db)):
    session = models.ShoppingSession(name=body.name, template_list_id=body.template_list_id)
    db.add(session)
    db.flush()

    if body.template_list_id:
        template = db.get(models.TemplateList, body.template_list_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        for item in template.items:
            db.add(models.SessionItem(
                session_id=session.id,
                name=item.name,
                category=item.category,
                position=item.position,
            ))

    db.commit()
    db.refresh(session)
    return session


@router.get("/{session_id}", response_model=schemas.ShoppingSession)
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = db.get(models.ShoppingSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.patch("/{session_id}", response_model=schemas.ShoppingSession)
def update_session(session_id: int, body: schemas.ShoppingSessionUpdate, db: Session = Depends(get_db)):
    session = db.get(models.ShoppingSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(session, field, value)
    db.commit()
    db.refresh(session)
    return session


@router.delete("/{session_id}", status_code=204)
def delete_session(session_id: int, db: Session = Depends(get_db)):
    session = db.get(models.ShoppingSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()


@router.post("/{session_id}/items", response_model=schemas.SessionItem, status_code=201)
def add_session_item(session_id: int, body: schemas.SessionItemCreate, db: Session = Depends(get_db)):
    session = db.get(models.ShoppingSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    item = models.SessionItem(session_id=session_id, **body.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{session_id}/items/{item_id}", response_model=schemas.SessionItem)
def update_session_item(session_id: int, item_id: int, body: schemas.SessionItemUpdate, db: Session = Depends(get_db)):
    item = db.get(models.SessionItem, item_id)
    if not item or item.session_id != session_id:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{session_id}/items/{item_id}", status_code=204)
def delete_session_item(session_id: int, item_id: int, db: Session = Depends(get_db)):
    item = db.get(models.SessionItem, item_id)
    if not item or item.session_id != session_id:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()

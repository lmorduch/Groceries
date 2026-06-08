# ABOUTME: Routes for shopping sessions - spawning from templates and tracking item state
# ABOUTME: Auto-sorts items into store sections on creation and when items are added

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db
from sorting import auto_sort_items

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _get_sections(store_id: int | None, db: Session) -> list[models.StoreSection]:
    if not store_id:
        return []
    store = db.get(models.Store, store_id)
    return store.sections if store else []


@router.get("/", response_model=list[schemas.ShoppingSession])
def list_sessions(db: Session = Depends(get_db)):
    return db.query(models.ShoppingSession).order_by(models.ShoppingSession.date.desc()).all()


@router.post("/", response_model=schemas.ShoppingSession, status_code=201)
def create_session(body: schemas.ShoppingSessionCreate, db: Session = Depends(get_db)):
    if body.store_id and not db.get(models.Store, body.store_id):
        raise HTTPException(status_code=404, detail="Store not found")

    session = models.ShoppingSession(
        name=body.name,
        template_list_id=body.template_list_id,
        store_id=body.store_id,
    )
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
        db.flush()

    # Auto-sort all items into sections
    db.refresh(session)
    sections = _get_sections(body.store_id, db)
    if sections:
        auto_sort_items(session.items, sections, skip_overridden=False)

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

    store_changing = "store_id" in body.model_dump(exclude_unset=True) and body.store_id != session.store_id

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(session, field, value)

    # Re-sort all non-overridden items when the store changes
    if store_changing:
        db.flush()
        sections = _get_sections(session.store_id, db)
        auto_sort_items(session.items, sections, skip_overridden=True)

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
    db.flush()

    # Auto-sort the new item if the session has a store
    sections = _get_sections(session.store_id, db)
    if sections:
        auto_sort_items([item], sections, skip_overridden=False)

    db.commit()
    db.refresh(item)
    return item


@router.patch("/{session_id}/items/{item_id}", response_model=schemas.SessionItem)
def update_session_item(session_id: int, item_id: int, body: schemas.SessionItemUpdate, db: Session = Depends(get_db)):
    item = db.get(models.SessionItem, item_id)
    if not item or item.session_id != session_id:
        raise HTTPException(status_code=404, detail="Item not found")

    updates = body.model_dump(exclude_unset=True)

    # If the caller is explicitly setting a section, mark it as overridden
    if "store_section_id" in updates and "section_overridden" not in updates:
        updates["section_overridden"] = True

    for field, value in updates.items():
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

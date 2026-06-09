# ABOUTME: Routes for shopping sessions - spawning from templates and tracking item state
# ABOUTME: Auto-sorts items into store sections on creation and when items are added, scoped per user

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from auth import get_current_user
from database import get_db
from sorting import auto_sort_items

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _user_email(user_id: int, db: Session) -> str:
    user = db.get(models.User, user_id)
    return user.email.lower() if user else ""


def _has_share(resource_type: str, resource_id: int, email: str, db: Session) -> bool:
    return db.query(models.Share).filter_by(
        resource_type=resource_type, resource_id=resource_id, shared_with_email=email
    ).first() is not None


def _get_session_or_404(
    session_id: int, user_id: int, db: Session, owner_only: bool = False
) -> models.ShoppingSession:
    s = db.get(models.ShoppingSession, session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    if s.user_id == user_id:
        return s
    if not owner_only and _has_share("session", session_id, _user_email(user_id, db), db):
        return s
    raise HTTPException(status_code=404, detail="Session not found")


def _get_sections(store_id: int | None, db: Session) -> list[models.StoreSection]:
    if not store_id:
        return []
    store = db.get(models.Store, store_id)
    return store.sections if store else []


@router.get("/", response_model=list[schemas.ShoppingSession])
def list_sessions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    uid = current_user["user_id"]
    email = _user_email(uid, db)
    shared_ids = [
        r.resource_id for r in
        db.query(models.Share).filter_by(resource_type="session", shared_with_email=email).all()
    ]
    from sqlalchemy import or_
    return (
        db.query(models.ShoppingSession)
        .filter(or_(models.ShoppingSession.user_id == uid, models.ShoppingSession.id.in_(shared_ids)))
        .order_by(models.ShoppingSession.date.desc())
        .all()
    )


@router.post("/", response_model=schemas.ShoppingSession, status_code=201)
def create_session(
    body: schemas.ShoppingSessionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    uid = current_user["user_id"]

    if body.store_id:
        store = db.get(models.Store, body.store_id)
        if not store or store.user_id != uid:
            raise HTTPException(status_code=404, detail="Store not found")

    session = models.ShoppingSession(
        name=body.name,
        user_id=uid,
        template_list_id=body.template_list_id,
        store_id=body.store_id,
    )
    db.add(session)
    db.flush()

    if body.template_list_id:
        template = db.get(models.TemplateList, body.template_list_id)
        if not template or template.user_id != uid:
            raise HTTPException(status_code=404, detail="Template not found")
        for item in template.items:
            db.add(models.SessionItem(
                session_id=session.id,
                name=item.name,
                category=item.category,
                position=item.position,
            ))
        db.flush()

    db.refresh(session)
    sections = _get_sections(body.store_id, db)
    if sections:
        auto_sort_items(session.items, sections, skip_overridden=False)

    db.commit()
    db.refresh(session)
    return session


@router.get("/{session_id}", response_model=schemas.ShoppingSession)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return _get_session_or_404(session_id, current_user["user_id"], db)


@router.patch("/{session_id}", response_model=schemas.ShoppingSession)
def update_session(
    session_id: int,
    body: schemas.ShoppingSessionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    session = _get_session_or_404(session_id, current_user["user_id"], db)

    store_changing = "store_id" in body.model_dump(exclude_unset=True) and body.store_id != session.store_id
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(session, field, value)

    if store_changing:
        db.flush()
        sections = _get_sections(session.store_id, db)
        auto_sort_items(session.items, sections, skip_overridden=True)

    db.commit()
    db.refresh(session)
    return session


@router.delete("/{session_id}", status_code=204)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    session = _get_session_or_404(session_id, current_user["user_id"], db, owner_only=True)
    db.delete(session)
    db.commit()


@router.post("/{session_id}/items", response_model=schemas.SessionItem, status_code=201)
def add_session_item(
    session_id: int,
    body: schemas.SessionItemCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    session = _get_session_or_404(session_id, current_user["user_id"], db)
    item = models.SessionItem(session_id=session_id, **body.model_dump())
    db.add(item)
    db.flush()

    sections = _get_sections(session.store_id, db)
    if sections:
        auto_sort_items([item], sections, skip_overridden=False)

    db.commit()
    db.refresh(item)
    return item


@router.patch("/{session_id}/items/{item_id}", response_model=schemas.SessionItem)
def update_session_item(
    session_id: int,
    item_id: int,
    body: schemas.SessionItemUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    _get_session_or_404(session_id, current_user["user_id"], db)
    item = db.get(models.SessionItem, item_id)
    if not item or item.session_id != session_id:
        raise HTTPException(status_code=404, detail="Item not found")

    updates = body.model_dump(exclude_unset=True)
    if "store_section_id" in updates and "section_overridden" not in updates:
        updates["section_overridden"] = True

    for field, value in updates.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{session_id}/items/{item_id}", status_code=204)
def delete_session_item(
    session_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    _get_session_or_404(session_id, current_user["user_id"], db)
    item = db.get(models.SessionItem, item_id)
    if not item or item.session_id != session_id:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()

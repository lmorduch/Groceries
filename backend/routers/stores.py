# ABOUTME: CRUD routes for stores, their sections, and section keywords
# ABOUTME: Keywords are used to auto-assign session items to sections, scoped per user

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from auth import get_current_user
from database import get_db

router = APIRouter(prefix="/stores", tags=["stores"])


def _user_email(user_id: int, db: Session) -> str:
    user = db.get(models.User, user_id)
    return user.email.lower() if user else ""


def _has_share(resource_type: str, resource_id: int, email: str, db: Session) -> bool:
    return db.query(models.Share).filter_by(
        resource_type=resource_type, resource_id=resource_id, shared_with_email=email
    ).first() is not None


def _get_store_or_404(
    store_id: int, user_id: int, db: Session, owner_only: bool = False
) -> models.Store:
    store = db.get(models.Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    if store.user_id == user_id:
        return store
    if not owner_only and _has_share("store", store_id, _user_email(user_id, db), db):
        return store
    raise HTTPException(status_code=404, detail="Store not found")


def _get_section_or_404(store: models.Store, section_id: int) -> models.StoreSection:
    section = next((s for s in store.sections if s.id == section_id), None)
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    return section


@router.get("/", response_model=list[schemas.Store])
def list_stores(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    uid = current_user["user_id"]
    email = _user_email(uid, db)
    shared_ids = [
        r.resource_id for r in
        db.query(models.Share).filter_by(resource_type="store", shared_with_email=email).all()
    ]
    from sqlalchemy import or_
    return (
        db.query(models.Store)
        .filter(or_(models.Store.user_id == uid, models.Store.id.in_(shared_ids)))
        .order_by(models.Store.name)
        .all()
    )


@router.post("/", response_model=schemas.Store, status_code=201)
def create_store(
    body: schemas.StoreCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    store = models.Store(name=body.name, user_id=current_user["user_id"])
    db.add(store)
    db.commit()
    db.refresh(store)
    return store


@router.get("/{store_id}", response_model=schemas.Store)
def get_store(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return _get_store_or_404(store_id, current_user["user_id"], db)


@router.patch("/{store_id}", response_model=schemas.Store)
def update_store(
    store_id: int,
    body: schemas.StoreUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    store = _get_store_or_404(store_id, current_user["user_id"], db)
    if body.name is not None:
        store.name = body.name
    db.commit()
    db.refresh(store)
    return store


@router.delete("/{store_id}", status_code=204)
def delete_store(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    store = _get_store_or_404(store_id, current_user["user_id"], db, owner_only=True)
    db.delete(store)
    db.commit()


@router.post("/{store_id}/sections", response_model=schemas.StoreSection, status_code=201)
def add_section(
    store_id: int,
    body: schemas.StoreSectionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    store = _get_store_or_404(store_id, current_user["user_id"], db)
    section = models.StoreSection(store_id=store_id, name=body.name, position=body.position)
    db.add(section)
    db.flush()
    for kw in body.keywords:
        db.add(models.SectionKeyword(section_id=section.id, keyword=kw.keyword.lower().strip()))
    db.commit()
    db.refresh(section)
    return section


@router.patch("/{store_id}/sections/{section_id}", response_model=schemas.StoreSection)
def update_section(
    store_id: int,
    section_id: int,
    body: schemas.StoreSectionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    store = _get_store_or_404(store_id, current_user["user_id"], db)
    section = _get_section_or_404(store, section_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(section, field, value)
    db.commit()
    db.refresh(section)
    return section


@router.delete("/{store_id}/sections/{section_id}", status_code=204)
def delete_section(
    store_id: int,
    section_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    store = _get_store_or_404(store_id, current_user["user_id"], db)
    section = _get_section_or_404(store, section_id)
    db.delete(section)
    db.commit()


@router.post("/{store_id}/sections/{section_id}/keywords", response_model=schemas.SectionKeyword, status_code=201)
def add_keyword(
    store_id: int,
    section_id: int,
    body: schemas.SectionKeywordCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    store = _get_store_or_404(store_id, current_user["user_id"], db)
    section = _get_section_or_404(store, section_id)
    kw = models.SectionKeyword(section_id=section.id, keyword=body.keyword.lower().strip())
    db.add(kw)
    db.commit()
    db.refresh(kw)
    return kw


@router.delete("/{store_id}/sections/{section_id}/keywords/{keyword_id}", status_code=204)
def delete_keyword(
    store_id: int,
    section_id: int,
    keyword_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    store = _get_store_or_404(store_id, current_user["user_id"], db)
    section = _get_section_or_404(store, section_id)
    kw = db.get(models.SectionKeyword, keyword_id)
    if not kw or kw.section_id != section.id:
        raise HTTPException(status_code=404, detail="Keyword not found")
    db.delete(kw)
    db.commit()

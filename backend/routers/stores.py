# ABOUTME: CRUD routes for stores, their sections, and section keywords
# ABOUTME: Keywords are used to auto-assign session items to sections

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/stores", tags=["stores"])


@router.get("/", response_model=list[schemas.Store])
def list_stores(db: Session = Depends(get_db)):
    return db.query(models.Store).order_by(models.Store.name).all()


@router.post("/", response_model=schemas.Store, status_code=201)
def create_store(body: schemas.StoreCreate, db: Session = Depends(get_db)):
    store = models.Store(name=body.name)
    db.add(store)
    db.commit()
    db.refresh(store)
    return store


@router.get("/{store_id}", response_model=schemas.Store)
def get_store(store_id: int, db: Session = Depends(get_db)):
    store = db.get(models.Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


@router.patch("/{store_id}", response_model=schemas.Store)
def update_store(store_id: int, body: schemas.StoreUpdate, db: Session = Depends(get_db)):
    store = db.get(models.Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    if body.name is not None:
        store.name = body.name
    db.commit()
    db.refresh(store)
    return store


@router.delete("/{store_id}", status_code=204)
def delete_store(store_id: int, db: Session = Depends(get_db)):
    store = db.get(models.Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    db.delete(store)
    db.commit()


# --- Sections ---

@router.post("/{store_id}/sections", response_model=schemas.StoreSection, status_code=201)
def add_section(store_id: int, body: schemas.StoreSectionCreate, db: Session = Depends(get_db)):
    store = db.get(models.Store, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    section = models.StoreSection(store_id=store_id, name=body.name, position=body.position)
    db.add(section)
    db.flush()
    for kw in body.keywords:
        db.add(models.SectionKeyword(section_id=section.id, keyword=kw.keyword.lower().strip()))
    db.commit()
    db.refresh(section)
    return section


@router.patch("/{store_id}/sections/{section_id}", response_model=schemas.StoreSection)
def update_section(store_id: int, section_id: int, body: schemas.StoreSectionUpdate, db: Session = Depends(get_db)):
    section = db.get(models.StoreSection, section_id)
    if not section or section.store_id != store_id:
        raise HTTPException(status_code=404, detail="Section not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(section, field, value)
    db.commit()
    db.refresh(section)
    return section


@router.delete("/{store_id}/sections/{section_id}", status_code=204)
def delete_section(store_id: int, section_id: int, db: Session = Depends(get_db)):
    section = db.get(models.StoreSection, section_id)
    if not section or section.store_id != store_id:
        raise HTTPException(status_code=404, detail="Section not found")
    db.delete(section)
    db.commit()


# --- Keywords ---

@router.post("/{store_id}/sections/{section_id}/keywords", response_model=schemas.SectionKeyword, status_code=201)
def add_keyword(store_id: int, section_id: int, body: schemas.SectionKeywordCreate, db: Session = Depends(get_db)):
    section = db.get(models.StoreSection, section_id)
    if not section or section.store_id != store_id:
        raise HTTPException(status_code=404, detail="Section not found")
    kw = models.SectionKeyword(section_id=section_id, keyword=body.keyword.lower().strip())
    db.add(kw)
    db.commit()
    db.refresh(kw)
    return kw


@router.delete("/{store_id}/sections/{section_id}/keywords/{keyword_id}", status_code=204)
def delete_keyword(store_id: int, section_id: int, keyword_id: int, db: Session = Depends(get_db)):
    kw = db.get(models.SectionKeyword, keyword_id)
    if not kw or kw.section_id != section_id:
        raise HTTPException(status_code=404, detail="Keyword not found")
    db.delete(kw)
    db.commit()

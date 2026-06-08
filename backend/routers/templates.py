# ABOUTME: CRUD routes for template lists and their items
# ABOUTME: Templates are reusable shopping list definitions

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/", response_model=list[schemas.TemplateList])
def list_templates(db: Session = Depends(get_db)):
    return db.query(models.TemplateList).order_by(models.TemplateList.name).all()


@router.post("/", response_model=schemas.TemplateList, status_code=201)
def create_template(body: schemas.TemplateListCreate, db: Session = Depends(get_db)):
    template = models.TemplateList(name=body.name)
    db.add(template)
    db.flush()
    for i, item in enumerate(body.items):
        db.add(models.TemplateItem(
            template_list_id=template.id,
            name=item.name,
            category=item.category,
            position=item.position if item.position else i,
        ))
    db.commit()
    db.refresh(template)
    return template


@router.get("/{template_id}", response_model=schemas.TemplateList)
def get_template(template_id: int, db: Session = Depends(get_db)):
    template = db.get(models.TemplateList, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.patch("/{template_id}", response_model=schemas.TemplateList)
def update_template(template_id: int, body: schemas.TemplateListUpdate, db: Session = Depends(get_db)):
    template = db.get(models.TemplateList, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if body.name is not None:
        template.name = body.name
    db.commit()
    db.refresh(template)
    return template


@router.delete("/{template_id}", status_code=204)
def delete_template(template_id: int, db: Session = Depends(get_db)):
    template = db.get(models.TemplateList, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    db.delete(template)
    db.commit()


@router.post("/{template_id}/items", response_model=schemas.TemplateItem, status_code=201)
def add_template_item(template_id: int, body: schemas.TemplateItemCreate, db: Session = Depends(get_db)):
    template = db.get(models.TemplateList, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    item = models.TemplateItem(template_list_id=template_id, **body.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{template_id}/items/{item_id}", response_model=schemas.TemplateItem)
def update_template_item(template_id: int, item_id: int, body: schemas.TemplateItemUpdate, db: Session = Depends(get_db)):
    item = db.get(models.TemplateItem, item_id)
    if not item or item.template_list_id != template_id:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{template_id}/items/{item_id}", status_code=204)
def delete_template_item(template_id: int, item_id: int, db: Session = Depends(get_db)):
    item = db.get(models.TemplateItem, item_id)
    if not item or item.template_list_id != template_id:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()

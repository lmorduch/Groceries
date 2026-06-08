# ABOUTME: Routes for pre-shopping inventory checks
# ABOUTME: Lets you record what you already have at home before creating a session, scoped per user

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from auth import get_current_user
from database import get_db

router = APIRouter(prefix="/inventory", tags=["inventory"])


def _get_check_or_404(check_id: int, user_id: int, db: Session) -> models.InventoryCheck:
    check = db.get(models.InventoryCheck, check_id)
    if not check or check.user_id != user_id:
        raise HTTPException(status_code=404, detail="Inventory check not found")
    return check


@router.get("/", response_model=list[schemas.InventoryCheck])
def list_inventory(
    session_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    q = db.query(models.InventoryCheck).filter_by(user_id=current_user["user_id"])
    if session_id is not None:
        q = q.filter(models.InventoryCheck.session_id == session_id)
    return q.order_by(models.InventoryCheck.created_at.desc()).all()


@router.post("/", response_model=schemas.InventoryCheck, status_code=201)
def create_inventory_check(
    body: schemas.InventoryCheckCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    check = models.InventoryCheck(user_id=current_user["user_id"], **body.model_dump())
    db.add(check)
    db.commit()
    db.refresh(check)
    return check


@router.patch("/{check_id}", response_model=schemas.InventoryCheck)
def update_inventory_check(
    check_id: int,
    body: schemas.InventoryCheckUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    check = _get_check_or_404(check_id, current_user["user_id"], db)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(check, field, value)
    db.commit()
    db.refresh(check)
    return check


@router.delete("/{check_id}", status_code=204)
def delete_inventory_check(
    check_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    check = _get_check_or_404(check_id, current_user["user_id"], db)
    db.delete(check)
    db.commit()

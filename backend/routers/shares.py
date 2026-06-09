# ABOUTME: Routes for sharing templates, sessions, and stores with other users by email
# ABOUTME: Only the owner of a resource can manage its shares

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from auth import get_current_user
from database import get_db

router = APIRouter(prefix="/shares", tags=["shares"])

VALID_TYPES = {"template", "session", "store"}


def _get_owner_id(resource_type: str, resource_id: int, db: Session) -> int | None:
    """Return the user_id of whoever owns this resource, or None if it doesn't exist."""
    if resource_type == "template":
        obj = db.get(models.TemplateList, resource_id)
    elif resource_type == "session":
        obj = db.get(models.ShoppingSession, resource_id)
    elif resource_type == "store":
        obj = db.get(models.Store, resource_id)
    else:
        return None
    return obj.user_id if obj else None


@router.get("/", response_model=list[schemas.Share])
def list_shares(
    resource_type: str,
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if resource_type not in VALID_TYPES:
        raise HTTPException(400, f"resource_type must be one of {VALID_TYPES}")
    owner_id = _get_owner_id(resource_type, resource_id, db)
    if owner_id != current_user["user_id"]:
        raise HTTPException(404, "Resource not found")
    return (
        db.query(models.Share)
        .filter_by(resource_type=resource_type, resource_id=resource_id)
        .all()
    )


@router.post("/", response_model=schemas.Share, status_code=201)
def create_share(
    body: schemas.ShareCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if body.resource_type not in VALID_TYPES:
        raise HTTPException(400, f"resource_type must be one of {VALID_TYPES}")

    owner_id = _get_owner_id(body.resource_type, body.resource_id, db)
    if owner_id != current_user["user_id"]:
        raise HTTPException(404, "Resource not found")

    email = body.email.lower().strip()

    # Don't let owners share with themselves
    owner = db.get(models.User, current_user["user_id"])
    if owner and owner.email.lower() == email:
        raise HTTPException(400, "You already own this resource")

    # Check the target user exists
    target = db.query(models.User).filter_by(email=email).first()
    if not target:
        raise HTTPException(404, f"No user found with email {body.email}. They need to sign in first.")

    # Don't create duplicate shares
    existing = db.query(models.Share).filter_by(
        resource_type=body.resource_type,
        resource_id=body.resource_id,
        shared_with_email=email,
    ).first()
    if existing:
        return existing

    share = models.Share(
        resource_type=body.resource_type,
        resource_id=body.resource_id,
        owner_user_id=current_user["user_id"],
        shared_with_email=email,
    )
    db.add(share)
    db.commit()
    db.refresh(share)
    return share


@router.delete("/{share_id}", status_code=204)
def delete_share(
    share_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    share = db.get(models.Share, share_id)
    if not share or share.owner_user_id != current_user["user_id"]:
        raise HTTPException(404, "Share not found")
    db.delete(share)
    db.commit()

# ABOUTME: Routes for pre-shopping inventory checks
# ABOUTME: Lets you record what you already have at home before creating a session, scoped per user

import base64
import json

import google.generativeai as genai
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

import models
import schemas
from auth import get_current_user
from crypto import decrypt
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


@router.post("/analyze-photo", response_model=list[str])
async def analyze_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = db.get(models.User, current_user["user_id"])
    if not user or not user.gemini_api_key:
        raise HTTPException(status_code=402, detail="Gemini API key not set. Add it in Settings.")

    image_data = await file.read()
    media_type = file.content_type or "image/jpeg"

    api_key = decrypt(user.gemini_api_key)
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content([
        {"mime_type": media_type, "data": base64.b64encode(image_data).decode()},
        (
            "List all food and grocery items visible in this image. "
            "Return ONLY a JSON array of item name strings, nothing else. "
            'Example: ["milk", "eggs", "bread"]'
        ),
    ])
    text = response.text
    # Strip markdown code fences if the model wraps the JSON
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(text)


@router.delete("/{check_id}", status_code=204)
def delete_inventory_check(
    check_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    check = _get_check_or_404(check_id, current_user["user_id"], db)
    db.delete(check)
    db.commit()

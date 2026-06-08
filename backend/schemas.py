# ABOUTME: Pydantic schemas for request/response validation
# ABOUTME: Mirrors models.py with separate Create/Update/Read shapes

from datetime import datetime

from pydantic import BaseModel


# --- Template Items ---

class TemplateItemCreate(BaseModel):
    name: str
    category: str | None = None
    position: int = 0


class TemplateItemUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    position: int | None = None


class TemplateItem(BaseModel):
    id: int
    template_list_id: int
    name: str
    category: str | None
    position: int

    model_config = {"from_attributes": True}


# --- Template Lists ---

class TemplateListCreate(BaseModel):
    name: str
    items: list[TemplateItemCreate] = []


class TemplateListUpdate(BaseModel):
    name: str | None = None


class TemplateList(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    items: list[TemplateItem] = []

    model_config = {"from_attributes": True}


# --- Session Items ---

class SessionItemCreate(BaseModel):
    name: str
    category: str | None = None
    position: int = 0


class SessionItemUpdate(BaseModel):
    checked: bool | None = None
    in_cart: bool | None = None
    name: str | None = None
    category: str | None = None


class SessionItem(BaseModel):
    id: int
    session_id: int
    name: str
    category: str | None
    position: int
    checked: bool
    in_cart: bool

    model_config = {"from_attributes": True}


# --- Shopping Sessions ---

class ShoppingSessionCreate(BaseModel):
    name: str
    template_list_id: int | None = None


class ShoppingSessionUpdate(BaseModel):
    name: str | None = None
    completed: bool | None = None


class ShoppingSession(BaseModel):
    id: int
    template_list_id: int | None
    name: str
    date: datetime
    completed: bool
    created_at: datetime
    items: list[SessionItem] = []

    model_config = {"from_attributes": True}


# --- Inventory Checks ---

class InventoryCheckCreate(BaseModel):
    name: str
    session_id: int | None = None
    notes: str | None = None


class InventoryCheckUpdate(BaseModel):
    have_it: bool | None = None
    notes: str | None = None


class InventoryCheck(BaseModel):
    id: int
    session_id: int | None
    name: str
    have_it: bool | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

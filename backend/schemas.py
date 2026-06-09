# ABOUTME: Pydantic schemas for request/response validation
# ABOUTME: Mirrors models.py with separate Create/Update/Read shapes

from datetime import datetime

from pydantic import BaseModel, Field


# --- Stores ---

class SectionKeywordCreate(BaseModel):
    keyword: str


class SectionKeyword(BaseModel):
    id: int
    section_id: int
    keyword: str

    model_config = {"from_attributes": True}


class StoreSectionCreate(BaseModel):
    name: str
    position: int = 0
    keywords: list[SectionKeywordCreate] = []


class StoreSectionUpdate(BaseModel):
    name: str | None = None
    position: int | None = None


class StoreSection(BaseModel):
    id: int
    store_id: int
    name: str
    position: int
    keywords: list[SectionKeyword] = []

    model_config = {"from_attributes": True}


class StoreCreate(BaseModel):
    name: str


class StoreUpdate(BaseModel):
    name: str | None = None


class Store(BaseModel):
    id: int
    owner_user_id: int = Field(alias="user_id")
    name: str
    sections: list[StoreSection] = []

    model_config = {"from_attributes": True, "populate_by_name": True}


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
    owner_user_id: int = Field(alias="user_id")
    name: str
    created_at: datetime
    updated_at: datetime
    items: list[TemplateItem] = []

    model_config = {"from_attributes": True, "populate_by_name": True}


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
    store_section_id: int | None = None
    section_overridden: bool | None = None


class SessionItem(BaseModel):
    id: int
    session_id: int
    name: str
    category: str | None
    position: int
    checked: bool
    in_cart: bool
    store_section_id: int | None
    section_overridden: bool

    model_config = {"from_attributes": True}


# --- Shopping Sessions ---

class ShoppingSessionCreate(BaseModel):
    name: str
    template_list_id: int | None = None
    store_id: int | None = None


class ShoppingSessionUpdate(BaseModel):
    name: str | None = None
    completed: bool | None = None
    store_id: int | None = None


class ShoppingSession(BaseModel):
    id: int
    owner_user_id: int = Field(alias="user_id")
    template_list_id: int | None
    store_id: int | None
    name: str
    date: datetime
    completed: bool
    created_at: datetime
    items: list[SessionItem] = []

    model_config = {"from_attributes": True, "populate_by_name": True}


# --- Shares ---

class ShareCreate(BaseModel):
    resource_type: str
    resource_id: int
    email: str


class Share(BaseModel):
    id: int
    resource_type: str
    resource_id: int
    shared_with_email: str

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

# ABOUTME: SQLAlchemy ORM models for grocery lists, sessions, and inventory
# ABOUTME: Entities: TemplateList, ShoppingSession, InventoryCheck, Store, StoreSection

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    google_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    picture: Mapped[str | None] = mapped_column(String, nullable=True)

    template_lists: Mapped[list["TemplateList"]] = relationship("TemplateList", back_populates="user")
    stores: Mapped[list["Store"]] = relationship("Store", back_populates="user")
    sessions: Mapped[list["ShoppingSession"]] = relationship("ShoppingSession", back_populates="user")
    inventory_checks: Mapped[list["InventoryCheck"]] = relationship("InventoryCheck", back_populates="user")


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="stores")

    sections: Mapped[list["StoreSection"]] = relationship(
        "StoreSection", back_populates="store", cascade="all, delete-orphan",
        order_by="StoreSection.position",
    )
    sessions: Mapped[list["ShoppingSession"]] = relationship("ShoppingSession", back_populates="store")


class StoreSection(Base):
    __tablename__ = "store_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(Integer, ForeignKey("stores.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0)

    store: Mapped["Store"] = relationship("Store", back_populates="sections")
    keywords: Mapped[list["SectionKeyword"]] = relationship(
        "SectionKeyword", back_populates="section", cascade="all, delete-orphan",
    )
    session_items: Mapped[list["SessionItem"]] = relationship("SessionItem", back_populates="store_section")


class SectionKeyword(Base):
    __tablename__ = "section_keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    section_id: Mapped[int] = mapped_column(Integer, ForeignKey("store_sections.id"), nullable=False)
    keyword: Mapped[str] = mapped_column(String, nullable=False)

    section: Mapped["StoreSection"] = relationship("StoreSection", back_populates="keywords")


class TemplateList(Base):
    __tablename__ = "template_lists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="template_lists")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    items: Mapped[list["TemplateItem"]] = relationship("TemplateItem", back_populates="template_list", cascade="all, delete-orphan", order_by="TemplateItem.position")
    sessions: Mapped[list["ShoppingSession"]] = relationship("ShoppingSession", back_populates="template_list")


class TemplateItem(Base):
    __tablename__ = "template_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    template_list_id: Mapped[int] = mapped_column(Integer, ForeignKey("template_lists.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    position: Mapped[int] = mapped_column(Integer, default=0)

    template_list: Mapped["TemplateList"] = relationship("TemplateList", back_populates="items")


class ShoppingSession(Base):
    __tablename__ = "shopping_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    template_list_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("template_lists.id"), nullable=True)
    store_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("stores.id"), nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="sessions")
    date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    template_list: Mapped["TemplateList | None"] = relationship("TemplateList", back_populates="sessions")
    store: Mapped["Store | None"] = relationship("Store", back_populates="sessions")
    items: Mapped[list["SessionItem"]] = relationship("SessionItem", back_populates="session", cascade="all, delete-orphan", order_by="SessionItem.position")


class SessionItem(Base):
    __tablename__ = "session_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("shopping_sessions.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str | None] = mapped_column(String, nullable=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    checked: Mapped[bool] = mapped_column(Boolean, default=False)
    in_cart: Mapped[bool] = mapped_column(Boolean, default=False)
    store_section_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("store_sections.id"), nullable=True)
    section_overridden: Mapped[bool] = mapped_column(Boolean, default=False)

    session: Mapped["ShoppingSession"] = relationship("ShoppingSession", back_populates="items")
    store_section: Mapped["StoreSection | None"] = relationship("StoreSection", back_populates="session_items")


class InventoryCheck(Base):
    __tablename__ = "inventory_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    session_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("shopping_sessions.id"), nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="inventory_checks")
    have_it: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

# ABOUTME: SQLAlchemy ORM models for grocery lists, sessions, and inventory
# ABOUTME: Three core entities: TemplateList, ShoppingSession, InventoryCheck

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class TemplateList(Base):
    __tablename__ = "template_lists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
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
    template_list_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("template_lists.id"), nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    template_list: Mapped["TemplateList | None"] = relationship("TemplateList", back_populates="sessions")
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

    session: Mapped["ShoppingSession"] = relationship("ShoppingSession", back_populates="items")


class InventoryCheck(Base):
    __tablename__ = "inventory_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("shopping_sessions.id"), nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    have_it: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

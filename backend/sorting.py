# ABOUTME: Auto-sorts session items into store sections based on keyword matching
# ABOUTME: Checks item name and category against each section's keywords in position order

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import models


def assign_section(item: "models.SessionItem", sections: list["models.StoreSection"]) -> int | None:
    """Return the section id that best matches item, or None if no match."""
    name_lower = item.name.lower()
    cat_lower = (item.category or "").lower()

    for section in sections:  # sections are already ordered by position
        for kw in section.keywords:
            if kw.keyword in name_lower or (cat_lower and kw.keyword in cat_lower):
                return section.id
    return None


def auto_sort_items(
    items: list["models.SessionItem"],
    sections: list["models.StoreSection"],
    skip_overridden: bool = True,
) -> None:
    """Mutate each item's store_section_id in place based on keyword matching.

    Items with section_overridden=True are left untouched when skip_overridden is True.
    """
    for item in items:
        if skip_overridden and item.section_overridden:
            continue
        item.store_section_id = assign_section(item, sections)

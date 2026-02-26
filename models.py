# models.py
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date
from enum import IntEnum


class CareerCategory(IntEnum):
    """Career value categories, ordered highest-value first (lowest number = best)."""
    PRINCIPAL = 1
    STUDENT_FILM = 2
    COMMERCIAL = 3
    SHORT_INDIE = 4
    BACKGROUND = 5
    OPEN_CALL = 6


TOP_FILM_SCHOOLS = {"usc", "ucla", "afi", "calarts", "cal arts", "chapman", "loyola marymount", "lmu"}


@dataclass
class CastingListing:
    title: str
    source: str
    url: str
    posted_date: date
    location: str
    union_status: str
    role_type: str
    description: str
    how_to_apply: str
    deadline: date | None = None
    compensation: str | None = None
    school_or_production: str | None = None

    def dedup_key(self) -> str:
        """Generate a deduplication key from URL and title."""
        raw = f"{self.url}|{self.title}".lower().strip()
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def categorize(self) -> CareerCategory:
        """Assign a career-value category to this listing."""
        text = f"{self.title} {self.description} {self.school_or_production or ''}".lower()

        # Check for top film school association
        if self.school_or_production:
            if self.school_or_production.lower() in TOP_FILM_SCHOOLS:
                return CareerCategory.STUDENT_FILM
        for school in TOP_FILM_SCHOOLS:
            if school in text:
                return CareerCategory.STUDENT_FILM

        role = self.role_type.lower()

        if role in ("principal", "lead", "supporting", "speaking"):
            return CareerCategory.PRINCIPAL

        if role == "commercial" or "commercial" in text:
            return CareerCategory.COMMERCIAL

        if role in ("background", "extra", "extras"):
            return CareerCategory.BACKGROUND

        if "open call" in text or "workshop" in text or role == "open call":
            return CareerCategory.OPEN_CALL

        # Default: short/indie
        return CareerCategory.SHORT_INDIE

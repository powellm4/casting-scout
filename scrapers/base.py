# scrapers/base.py
from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from models import CastingListing

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Interface all scrapers implement."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        ...

    @abstractmethod
    def scrape(self) -> list[CastingListing]:
        """Fetch and parse listings. Returns empty list on failure."""
        ...

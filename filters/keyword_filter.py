# filters/keyword_filter.py
from __future__ import annotations

from datetime import date, timedelta

from config import LA_METRO_LOCATIONS, NON_UNION_KEYWORDS, FRESHNESS_HOURS
from models import CastingListing


class KeywordFilter:
    """V1 filter: keyword matching on location, union status, freshness, and deadline."""

    def filter(self, listings: list[CastingListing]) -> list[CastingListing]:
        return [l for l in listings if self._passes(l)]

    def _passes(self, listing: CastingListing) -> bool:
        return (
            self._location_ok(listing)
            and self._union_ok(listing)
            and self._fresh_enough(listing)
            and self._not_expired(listing)
        )

    def _location_ok(self, listing: CastingListing) -> bool:
        loc = listing.location.lower()
        return any(city in loc for city in LA_METRO_LOCATIONS)

    def _union_ok(self, listing: CastingListing) -> bool:
        status = listing.union_status.lower().strip()
        if not status:
            return True  # unspecified passes
        return any(kw in status for kw in NON_UNION_KEYWORDS)

    def _fresh_enough(self, listing: CastingListing) -> bool:
        cutoff = date.today() - timedelta(hours=FRESHNESS_HOURS)
        return listing.posted_date >= cutoff

    def _not_expired(self, listing: CastingListing) -> bool:
        if listing.deadline is None:
            return True
        return listing.deadline >= date.today()

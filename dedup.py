# dedup.py
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from models import CastingListing


class Deduplicator:
    def __init__(self, seen_path: str):
        self._path = Path(seen_path)
        self._seen: dict[str, str] = self._load()

    def _load(self) -> dict[str, str]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._seen, indent=2))

    def deduplicate(self, listings: list[CastingListing]) -> list[CastingListing]:
        """Return only listings not previously seen. Also dedup within the batch."""
        result = []
        seen_in_batch: set[str] = set()
        for listing in listings:
            key = listing.dedup_key()
            if key not in self._seen and key not in seen_in_batch:
                result.append(listing)
                seen_in_batch.add(key)
        return result

    def mark_seen(self, listings: list[CastingListing]) -> None:
        """Record listings as seen and persist to disk."""
        today = date.today().isoformat()
        for listing in listings:
            self._seen[listing.dedup_key()] = today
        self._save()

    def cleanup(self, max_age_days: int = 30) -> None:
        """Remove seen entries older than max_age_days."""
        cutoff = date.today() - timedelta(days=max_age_days)
        self._seen = {
            k: v for k, v in self._seen.items()
            if date.fromisoformat(v) >= cutoff
        }
        self._save()

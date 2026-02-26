# tests/test_dedup.py
import json
import os
from datetime import date

from dedup import Deduplicator
from models import CastingListing


def _make_listing(title="Test", url="https://example.com/1", **kw) -> CastingListing:
    defaults = {
        "title": title,
        "source": "backstage",
        "url": url,
        "posted_date": date.today(),
        "location": "LA",
        "union_status": "non-union",
        "role_type": "principal",
        "description": "Test",
        "how_to_apply": "Apply",
    }
    defaults.update(kw)
    return CastingListing(**defaults)


def test_new_listings_pass_through(tmp_path):
    path = tmp_path / "seen.json"
    path.write_text("{}")
    d = Deduplicator(str(path))
    listings = [_make_listing(title="A", url="https://a.com"), _make_listing(title="B", url="https://b.com")]
    result = d.deduplicate(listings)
    assert len(result) == 2


def test_seen_listings_filtered_out(tmp_path):
    path = tmp_path / "seen.json"
    path.write_text("{}")
    d = Deduplicator(str(path))
    listing = _make_listing(title="A", url="https://a.com")

    # First pass: listing is new
    result1 = d.deduplicate([listing])
    assert len(result1) == 1
    d.mark_seen(result1)

    # Second pass: listing is seen
    result2 = d.deduplicate([listing])
    assert len(result2) == 0


def test_persistence_across_instances(tmp_path):
    path = tmp_path / "seen.json"
    path.write_text("{}")
    listing = _make_listing(title="A", url="https://a.com")

    d1 = Deduplicator(str(path))
    d1.deduplicate([listing])
    d1.mark_seen([listing])

    d2 = Deduplicator(str(path))
    result = d2.deduplicate([listing])
    assert len(result) == 0


def test_cross_source_dedup(tmp_path):
    """Same title+URL from different sources should dedup."""
    path = tmp_path / "seen.json"
    path.write_text("{}")
    d = Deduplicator(str(path))
    listing1 = _make_listing(title="Role X", url="https://example.com/role-x")
    listing2 = _make_listing(title="Role X", url="https://example.com/role-x", source="craigslist")
    result = d.deduplicate([listing1, listing2])
    assert len(result) == 1


def test_old_seen_entries_expire(tmp_path):
    """Seen entries older than 30 days should be cleaned up."""
    path = tmp_path / "seen.json"
    old_data = {"old_hash_123": "2026-01-01"}
    path.write_text(json.dumps(old_data))
    d = Deduplicator(str(path))
    d.cleanup(max_age_days=30)
    data = json.loads(path.read_text())
    assert "old_hash_123" not in data

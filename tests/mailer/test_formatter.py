# tests/mailer/test_formatter.py
from datetime import date

from mailer.formatter import format_digest
from models import CastingListing, CareerCategory


def _make_listing(title="Test", role_type="principal", **kw) -> CastingListing:
    defaults = {
        "title": title,
        "source": "backstage",
        "url": "https://backstage.com/1",
        "posted_date": date.today(),
        "location": "Los Angeles, CA",
        "union_status": "non-union",
        "role_type": role_type,
        "description": "Test description for this role.",
        "how_to_apply": "Apply online",
    }
    defaults.update(kw)
    return CastingListing(**defaults)


def test_format_digest_returns_subject_and_html():
    listings = [_make_listing(title="Lead Role")]
    subject, html = format_digest(listings)
    assert "1" in subject  # count
    assert "Lead Role" in html


def test_format_digest_groups_by_category():
    listings = [
        _make_listing(title="Lead Role", role_type="principal"),
        _make_listing(title="BG Extra", role_type="background", url="https://backstage.com/2"),
        _make_listing(title="TV Commercial", role_type="commercial", url="https://backstage.com/3"),
    ]
    subject, html = format_digest(listings)
    # Principal should appear before background in HTML
    principal_pos = html.index("Lead Role")
    bg_pos = html.index("BG Extra")
    assert principal_pos < bg_pos


def test_format_digest_includes_apply_link():
    listings = [_make_listing(how_to_apply="Apply at https://example.com")]
    _, html = format_digest(listings)
    assert "https://example.com" in html or "Apply" in html


def test_format_digest_empty_listings():
    subject, html = format_digest([])
    assert "0" in subject or "no new" in subject.lower() or "nothing" in html.lower()


def test_format_digest_shows_source():
    listings = [_make_listing(source="craigslist")]
    _, html = format_digest(listings)
    assert "craigslist" in html.lower() or "Craigslist" in html


def test_format_digest_flags_school():
    listings = [_make_listing(title="USC Film", school_or_production="USC")]
    _, html = format_digest(listings)
    assert "USC" in html

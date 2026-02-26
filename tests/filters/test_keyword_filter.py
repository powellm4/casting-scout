# tests/filters/test_keyword_filter.py
from datetime import date, timedelta

from filters.keyword_filter import KeywordFilter
from models import CastingListing


def _make_listing(**overrides) -> CastingListing:
    """Helper to create a CastingListing with sensible defaults."""
    defaults = {
        "title": "Test Role",
        "source": "backstage",
        "url": "https://backstage.com/test/1",
        "posted_date": date.today(),
        "location": "Los Angeles, CA",
        "union_status": "non-union",
        "role_type": "principal",
        "description": "Test description",
        "how_to_apply": "Apply online",
    }
    defaults.update(overrides)
    return CastingListing(**defaults)


class TestLocationFilter:
    def test_passes_los_angeles(self):
        f = KeywordFilter()
        listings = [_make_listing(location="Los Angeles, CA")]
        assert len(f.filter(listings)) == 1

    def test_passes_burbank(self):
        f = KeywordFilter()
        listings = [_make_listing(location="Burbank, CA")]
        assert len(f.filter(listings)) == 1

    def test_rejects_new_york(self):
        f = KeywordFilter()
        listings = [_make_listing(location="New York, NY")]
        assert len(f.filter(listings)) == 0

    def test_case_insensitive(self):
        f = KeywordFilter()
        listings = [_make_listing(location="HOLLYWOOD, CA")]
        assert len(f.filter(listings)) == 1


class TestUnionFilter:
    def test_passes_non_union(self):
        f = KeywordFilter()
        listings = [_make_listing(union_status="Non-Union")]
        assert len(f.filter(listings)) == 1

    def test_passes_open_to_all(self):
        f = KeywordFilter()
        listings = [_make_listing(union_status="Open to All")]
        assert len(f.filter(listings)) == 1

    def test_passes_unspecified(self):
        f = KeywordFilter()
        listings = [_make_listing(union_status="")]
        assert len(f.filter(listings)) == 1

    def test_rejects_sag_only(self):
        f = KeywordFilter()
        listings = [_make_listing(union_status="SAG-AFTRA only")]
        assert len(f.filter(listings)) == 0


class TestFreshnessFilter:
    def test_passes_today(self):
        f = KeywordFilter()
        listings = [_make_listing(posted_date=date.today())]
        assert len(f.filter(listings)) == 1

    def test_passes_yesterday(self):
        f = KeywordFilter()
        listings = [_make_listing(posted_date=date.today() - timedelta(days=1))]
        assert len(f.filter(listings)) == 1

    def test_rejects_old_listing(self):
        f = KeywordFilter()
        listings = [_make_listing(posted_date=date.today() - timedelta(days=5))]
        assert len(f.filter(listings)) == 0


class TestDeadlineFilter:
    def test_passes_future_deadline(self):
        f = KeywordFilter()
        listings = [_make_listing(deadline=date.today() + timedelta(days=7))]
        assert len(f.filter(listings)) == 1

    def test_passes_no_deadline(self):
        f = KeywordFilter()
        listings = [_make_listing(deadline=None)]
        assert len(f.filter(listings)) == 1

    def test_rejects_expired(self):
        f = KeywordFilter()
        listings = [_make_listing(deadline=date.today() - timedelta(days=1))]
        assert len(f.filter(listings)) == 0


class TestProfileFilter:
    def test_passes_generic_listing(self):
        f = KeywordFilter()
        listings = [_make_listing(title="Lead Role in Feature Film")]
        assert len(f.filter(listings)) == 1

    def test_rejects_female_listing(self):
        f = KeywordFilter()
        listings = [_make_listing(title="Seeking Female Models for Photoshoot")]
        assert len(f.filter(listings)) == 0

    def test_rejects_research_study(self):
        f = KeywordFilter()
        listings = [_make_listing(title="Paid Research Study - Beards Wanted")]
        assert len(f.filter(listings)) == 0

    def test_rejects_child_actor(self):
        f = KeywordFilter()
        listings = [_make_listing(title="PAID Child Actor Casting")]
        assert len(f.filter(listings)) == 0

    def test_rejects_focus_group(self):
        f = KeywordFilter()
        listings = [_make_listing(title="PAID FOCUS GROUP $100")]
        assert len(f.filter(listings)) == 0

    def test_passes_male_acting_role(self):
        f = KeywordFilter()
        listings = [_make_listing(title="Male Actor Needed for Comedy Short")]
        assert len(f.filter(listings)) == 1


class TestCombinedFilters:
    def test_multiple_listings_mixed(self):
        f = KeywordFilter()
        listings = [
            _make_listing(title="Good", location="Los Angeles, CA", union_status="non-union"),
            _make_listing(title="Wrong City", location="Chicago, IL", union_status="non-union"),
            _make_listing(title="Wrong Union", location="Burbank, CA", union_status="SAG-AFTRA only"),
            _make_listing(title="Also Good", location="Studio City, CA", union_status="Open to All"),
        ]
        result = f.filter(listings)
        titles = [l.title for l in result]
        assert "Good" in titles
        assert "Also Good" in titles
        assert "Wrong City" not in titles
        assert "Wrong Union" not in titles

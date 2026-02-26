# tests/test_models.py
from datetime import date

from models import CastingListing, CareerCategory


def test_casting_listing_creation():
    listing = CastingListing(
        title="Background for Netflix Drama",
        source="backstage",
        url="https://backstage.com/casting/123",
        posted_date=date(2026, 2, 25),
        location="Los Angeles, CA",
        union_status="non-union",
        role_type="background",
        description="Seeking diverse background for courtroom scenes.",
        how_to_apply="Submit via Backstage",
    )
    assert listing.title == "Background for Netflix Drama"
    assert listing.source == "backstage"
    assert listing.deadline is None
    assert listing.compensation is None
    assert listing.school_or_production is None


def test_casting_listing_with_all_fields():
    listing = CastingListing(
        title="Lead in USC Thesis Film",
        source="craigslist",
        url="https://losangeles.craigslist.org/tlnt/123",
        posted_date=date(2026, 2, 24),
        deadline=date(2026, 3, 1),
        location="Burbank, CA",
        union_status="non-union",
        role_type="principal",
        compensation="$100/day + meals",
        description="USC MFA thesis film seeking lead actor.",
        how_to_apply="Email headshot to director@usc.edu",
        school_or_production="USC",
    )
    assert listing.deadline == date(2026, 3, 1)
    assert listing.compensation == "$100/day + meals"
    assert listing.school_or_production == "USC"


def test_casting_listing_dedup_key():
    listing = CastingListing(
        title="Background for Netflix Drama",
        source="backstage",
        url="https://backstage.com/casting/123",
        posted_date=date(2026, 2, 25),
        location="Los Angeles, CA",
        union_status="non-union",
        role_type="background",
        description="Seeking diverse background.",
        how_to_apply="Submit via Backstage",
    )
    key = listing.dedup_key()
    assert isinstance(key, str)
    assert len(key) > 0
    # Same listing should produce same key
    assert listing.dedup_key() == key


def test_career_category_ordering():
    """Career categories should be ordered by career value (highest first)."""
    assert CareerCategory.PRINCIPAL.value < CareerCategory.STUDENT_FILM.value
    assert CareerCategory.STUDENT_FILM.value < CareerCategory.COMMERCIAL.value
    assert CareerCategory.COMMERCIAL.value < CareerCategory.SHORT_INDIE.value
    assert CareerCategory.SHORT_INDIE.value < CareerCategory.BACKGROUND.value
    assert CareerCategory.BACKGROUND.value < CareerCategory.OPEN_CALL.value


def test_casting_listing_categorize_principal():
    listing = CastingListing(
        title="Lead Role in Feature",
        source="backstage",
        url="https://backstage.com/1",
        posted_date=date(2026, 2, 25),
        location="LA",
        union_status="non-union",
        role_type="principal",
        description="Seeking lead.",
        how_to_apply="Apply online",
    )
    assert listing.categorize() == CareerCategory.PRINCIPAL


def test_casting_listing_categorize_student_film():
    listing = CastingListing(
        title="USC Thesis Film",
        source="craigslist",
        url="https://craigslist.org/1",
        posted_date=date(2026, 2, 25),
        location="LA",
        union_status="non-union",
        role_type="principal",
        description="USC MFA thesis film.",
        how_to_apply="Email",
        school_or_production="USC",
    )
    assert listing.categorize() == CareerCategory.STUDENT_FILM


def test_casting_listing_categorize_background():
    listing = CastingListing(
        title="Background Extras Needed",
        source="backstage",
        url="https://backstage.com/2",
        posted_date=date(2026, 2, 25),
        location="LA",
        union_status="non-union",
        role_type="background",
        description="Extras for TV show.",
        how_to_apply="Submit online",
    )
    assert listing.categorize() == CareerCategory.BACKGROUND

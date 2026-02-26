# tests/scrapers/test_backstage.py
from pathlib import Path

from scrapers.backstage import BackstageScraper

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_parse_listings_from_html():
    html = (FIXTURES / "backstage_sample.html").read_text()
    scraper = BackstageScraper()
    listings = scraper.parse_html(html)
    assert len(listings) >= 1
    for listing in listings:
        assert listing.source == "backstage"
        assert listing.url
        assert listing.title

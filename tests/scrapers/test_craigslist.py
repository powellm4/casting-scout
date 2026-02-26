# tests/scrapers/test_craigslist.py
from pathlib import Path

from scrapers.craigslist import CraigslistScraper


FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_parse_listings_from_html():
    html = (FIXTURES / "craigslist_sample.html").read_text()
    scraper = CraigslistScraper()
    listings = scraper.parse_html(html)
    assert len(listings) >= 1
    for listing in listings:
        assert listing.source == "craigslist"
        assert listing.url.startswith("http")
        assert listing.title


def test_parse_extracts_location():
    html = (FIXTURES / "craigslist_sample.html").read_text()
    scraper = CraigslistScraper()
    listings = scraper.parse_html(html)
    assert any(l.location for l in listings)

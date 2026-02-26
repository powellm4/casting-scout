# tests/scrapers/test_casting_networks.py
from pathlib import Path

from scrapers.casting_networks import CastingNetworksScraper

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_parse_listings_from_html():
    html = (FIXTURES / "casting_networks_sample.html").read_text()
    scraper = CastingNetworksScraper()
    listings = scraper.parse_html(html)
    assert len(listings) >= 1
    for listing in listings:
        assert listing.source == "casting_networks"
        assert listing.url
        assert listing.title

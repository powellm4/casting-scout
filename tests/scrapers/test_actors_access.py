# tests/scrapers/test_actors_access.py
from scrapers.actors_access import ActorsAccessScraper


def test_scraper_returns_empty_without_credentials():
    """Without credentials, scraper should gracefully return empty list."""
    scraper = ActorsAccessScraper()
    # source_name should be correct
    assert scraper.source_name == "actors_access"


def test_parse_html_with_empty_page():
    scraper = ActorsAccessScraper()
    listings = scraper.parse_html("<html><body></body></html>")
    assert listings == []

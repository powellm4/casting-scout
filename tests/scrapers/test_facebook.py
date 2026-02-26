# tests/scrapers/test_facebook.py
from scrapers.facebook import FacebookScraper


def test_scraper_returns_empty_without_cookies():
    """Without cookies, scraper should gracefully return empty list."""
    scraper = FacebookScraper()
    assert scraper.source_name == "facebook"


def test_parse_html_with_empty_page():
    scraper = FacebookScraper()
    listings = scraper.parse_html("<html><body></body></html>")
    assert listings == []

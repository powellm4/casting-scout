# tests/scrapers/test_reddit.py
import json
from pathlib import Path

from scrapers.reddit import RedditScraper

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_parse_subreddit_json():
    data = json.loads((FIXTURES / "reddit_sample.json").read_text())
    scraper = RedditScraper()
    listings = scraper.parse_json(data)
    assert len(listings) >= 1
    for listing in listings:
        assert listing.source == "reddit"
        assert listing.title
        assert listing.url


def test_parse_extracts_description():
    data = json.loads((FIXTURES / "reddit_sample.json").read_text())
    scraper = RedditScraper()
    listings = scraper.parse_json(data)
    assert any("actor" in l.description.lower() or "extras" in l.description.lower() for l in listings)

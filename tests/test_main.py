# tests/test_main.py
from datetime import date
from unittest.mock import patch, MagicMock

from main import run
from models import CastingListing


def _make_listing(title="Test", url="https://example.com/1") -> CastingListing:
    return CastingListing(
        title=title, source="test", url=url,
        posted_date=date.today(), location="Los Angeles, CA",
        union_status="non-union", role_type="principal",
        description="Test", how_to_apply="Apply",
    )


@patch("main.send_email", return_value=True)
@patch("main.Deduplicator")
@patch("main.KeywordFilter")
@patch("main.get_scrapers")
def test_run_orchestrates_scrape_filter_email(mock_scrapers, mock_filter_cls, mock_dedup_cls, mock_send):
    # Setup mock scraper
    scraper = MagicMock()
    scraper.source_name = "test"
    scraper.scrape.return_value = [_make_listing()]
    mock_scrapers.return_value = [scraper]

    # Setup mock filter
    mock_filter = MagicMock()
    mock_filter.filter.side_effect = lambda x: x
    mock_filter_cls.return_value = mock_filter

    # Setup mock dedup
    mock_dedup = MagicMock()
    mock_dedup.deduplicate.side_effect = lambda x: x
    mock_dedup_cls.return_value = mock_dedup

    with patch("main.SENDGRID_API_KEY", "fake"), patch("main.RECIPIENT_EMAIL", "test@test.com"):
        run()

    mock_send.assert_called_once()
    mock_dedup.mark_seen.assert_called_once()


@patch("main.send_email", return_value=True)
@patch("main.Deduplicator")
@patch("main.KeywordFilter")
@patch("main.get_scrapers")
def test_run_handles_scraper_failure(mock_scrapers, mock_filter_cls, mock_dedup_cls, mock_send):
    failing_scraper = MagicMock()
    failing_scraper.source_name = "broken"
    failing_scraper.scrape.side_effect = Exception("boom")

    working_scraper = MagicMock()
    working_scraper.source_name = "good"
    working_scraper.scrape.return_value = [_make_listing()]

    mock_scrapers.return_value = [failing_scraper, working_scraper]
    mock_filter_cls.return_value.filter.side_effect = lambda x: x
    mock_dedup_cls.return_value.deduplicate.side_effect = lambda x: x

    with patch("main.SENDGRID_API_KEY", "fake"), patch("main.RECIPIENT_EMAIL", "test@test.com"):
        run()

    # Email still sent despite one scraper failing
    mock_send.assert_called_once()

# main.py
from __future__ import annotations

import logging
import sys

from config import (
    SENDGRID_API_KEY, RECIPIENT_EMAIL, SENDER_EMAIL,
    SCRAPERS_ENABLED, SEEN_LISTINGS_PATH,
)
from dedup import Deduplicator
from mailer.formatter import format_digest
from mailer.sender import send_email
from filters.keyword_filter import KeywordFilter
from models import CastingListing
from scrapers.base import BaseScraper

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def get_scrapers() -> list[BaseScraper]:
    """Return enabled scraper instances."""
    scrapers: list[BaseScraper] = []
    if SCRAPERS_ENABLED.get("craigslist"):
        from scrapers.craigslist import CraigslistScraper
        scrapers.append(CraigslistScraper())
    if SCRAPERS_ENABLED.get("reddit"):
        from scrapers.reddit import RedditScraper
        scrapers.append(RedditScraper())
    if SCRAPERS_ENABLED.get("backstage"):
        from scrapers.backstage import BackstageScraper
        scrapers.append(BackstageScraper())
    if SCRAPERS_ENABLED.get("casting_networks"):
        from scrapers.casting_networks import CastingNetworksScraper
        scrapers.append(CastingNetworksScraper())
    if SCRAPERS_ENABLED.get("actors_access"):
        from scrapers.actors_access import ActorsAccessScraper
        scrapers.append(ActorsAccessScraper())
    if SCRAPERS_ENABLED.get("facebook"):
        from scrapers.facebook import FacebookScraper
        scrapers.append(FacebookScraper())
    return scrapers


def run() -> None:
    logger.info("Casting Scout starting...")

    # 1. Scrape all sources
    all_listings: list[CastingListing] = []
    failed_sources: list[str] = []

    for scraper in get_scrapers():
        try:
            logger.info(f"Scraping {scraper.source_name}...")
            listings = scraper.scrape()
            logger.info(f"  Found {len(listings)} listings from {scraper.source_name}")
            all_listings.extend(listings)
        except Exception:
            logger.exception(f"Scraper {scraper.source_name} failed")
            failed_sources.append(scraper.source_name)

    logger.info(f"Total raw listings: {len(all_listings)}")

    # 2. Filter
    f = KeywordFilter()
    filtered = f.filter(all_listings)
    logger.info(f"After filtering: {len(filtered)}")

    # 3. Deduplicate
    dedup = Deduplicator(SEEN_LISTINGS_PATH)
    dedup.cleanup()
    new_listings = dedup.deduplicate(filtered)
    logger.info(f"After dedup: {len(new_listings)}")

    # 4. Format email
    subject, html = format_digest(new_listings, failed_sources if failed_sources else None)

    # 5. Send (skip if all scrapers failed and no listings)
    if not all_listings and failed_sources:
        logger.error("All scrapers failed. No email sent.")
        sys.exit(1)

    if not SENDGRID_API_KEY or not RECIPIENT_EMAIL:
        logger.warning("SendGrid not configured. Printing email to stdout instead.")
        print(f"Subject: {subject}\n\n{html}")
    else:
        success = send_email(subject, html, SENDGRID_API_KEY, RECIPIENT_EMAIL, SENDER_EMAIL)
        if not success:
            logger.error("Failed to send email.")
            sys.exit(1)

    # 6. Mark as seen
    dedup.mark_seen(new_listings)
    logger.info(f"Done! Sent {len(new_listings)} listings.")


if __name__ == "__main__":
    run()

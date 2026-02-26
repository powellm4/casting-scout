# scrapers/facebook.py
from __future__ import annotations

import json
import logging
import os
from datetime import date

from bs4 import BeautifulSoup

from models import CastingListing
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

# Public casting groups in LA area
FACEBOOK_GROUPS = [
    "https://www.facebook.com/groups/lacastingcalls",
    "https://www.facebook.com/groups/actorsinla",
]


class FacebookScraper(BaseScraper):
    """Best-effort Facebook scraper. Highly fragile — Facebook blocks scrapers."""

    @property
    def source_name(self) -> str:
        return "facebook"

    def scrape(self) -> list[CastingListing]:
        cookies_json = os.environ.get("FACEBOOK_COOKIES", "")
        if not cookies_json:
            logger.info("Facebook cookies not configured, skipping")
            return []

        try:
            cookies = json.loads(cookies_json)
        except (json.JSONDecodeError, TypeError):
            logger.warning("Invalid Facebook cookies JSON")
            return []

        all_listings: list[CastingListing] = []
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()

                # Set stored cookies
                context.add_cookies(cookies)

                for group_url in FACEBOOK_GROUPS:
                    try:
                        page = context.new_page()
                        page.goto(group_url, wait_until="domcontentloaded", timeout=30000)
                        page.wait_for_timeout(3000)  # Allow JS to render
                        html = page.content()
                        page.close()
                        all_listings.extend(self.parse_html(html))
                    except Exception:
                        logger.exception(f"Facebook failed for {group_url}")
                        continue

                browser.close()
        except Exception:
            logger.exception("Facebook scraper failed")

        return all_listings

    def parse_html(self, html: str) -> list[CastingListing]:
        """Parse Facebook group posts. Very fragile — FB changes DOM constantly."""
        soup = BeautifulSoup(html, "html.parser")
        listings: list[CastingListing] = []

        # Facebook's DOM is heavily obfuscated. These selectors are best-effort.
        posts = soup.select("[data-ad-preview], [role='article']")
        for post in posts:
            try:
                text = post.get_text(" ", strip=True)
                if not text or len(text) < 20:
                    continue

                # Only include posts that seem casting-related
                casting_keywords = ["casting", "audition", "seeking", "looking for actors",
                                    "open call", "background", "extras", "role"]
                if not any(kw in text.lower() for kw in casting_keywords):
                    continue

                link = post.find("a", href=True)
                url = link["href"] if link else ""
                if url and not url.startswith("http"):
                    url = f"https://www.facebook.com{url}"

                title = text[:100].strip()

                listings.append(CastingListing(
                    title=title,
                    source="facebook",
                    url=url or "https://www.facebook.com",
                    posted_date=date.today(),
                    location="",  # Facebook posts rarely have structured location
                    union_status="",
                    role_type="other",
                    description=text[:500],
                    how_to_apply=f"See Facebook post: {url}" if url else "Check Facebook group",
                ))
            except Exception:
                logger.exception("Failed to parse Facebook post")
                continue

        return listings

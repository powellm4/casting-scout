# scrapers/backstage.py
from __future__ import annotations

import logging
from datetime import date, datetime

from bs4 import BeautifulSoup

from models import CastingListing
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

BACKSTAGE_URL = "https://www.backstage.com/casting/open-casting-calls-auditions/"


class BackstageScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return "backstage"

    def scrape(self) -> list[CastingListing]:
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(BACKSTAGE_URL, wait_until="networkidle", timeout=60000)
                html = page.content()
                browser.close()
                return self.parse_html(html)
        except Exception:
            logger.exception("Backstage scraper failed")
            return []

    def parse_html(self, html: str) -> list[CastingListing]:
        """Parse Backstage HTML. Selectors should be verified against live site."""
        soup = BeautifulSoup(html, "html.parser")
        listings: list[CastingListing] = []

        cards = soup.select("[data-testid='casting-card'], .casting-card, article.StyledCastingCard")
        for card in cards:
            try:
                link = card.find("a")
                if not link:
                    continue
                href = link.get("href", "")
                url = href if href.startswith("http") else f"https://www.backstage.com{href}"
                title = link.get_text(strip=True) or card.get_text(strip=True)[:100]
                if not title:
                    continue

                # Try to extract structured data from card details
                location_el = card.select_one(".location")
                location = location_el.get_text(strip=True) if location_el else "Los Angeles, CA"

                union_el = card.select_one(".union-status")
                union_status = union_el.get_text(strip=True) if union_el else "non-union"

                role_el = card.select_one(".role-type")
                role_type = role_el.get_text(strip=True).lower() if role_el else "other"

                listings.append(CastingListing(
                    title=title,
                    source="backstage",
                    url=url,
                    posted_date=date.today(),
                    location=location,
                    union_status=union_status,
                    role_type=role_type,
                    description=title,
                    how_to_apply=f"Apply on Backstage: {url}",
                ))
            except Exception:
                logger.exception("Failed to parse Backstage card")
                continue

        return listings

# scrapers/casting_networks.py
from __future__ import annotations

import logging
from datetime import date

from bs4 import BeautifulSoup

from models import CastingListing
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

CASTING_NETWORKS_URL = "https://www.castingnetworks.com/talent/casting"


class CastingNetworksScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return "casting_networks"

    def scrape(self) -> list[CastingListing]:
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(CASTING_NETWORKS_URL, wait_until="networkidle", timeout=60000)
                html = page.content()
                browser.close()
                return self.parse_html(html)
        except Exception:
            logger.exception("Casting Networks scraper failed")
            return []

    def parse_html(self, html: str) -> list[CastingListing]:
        """Parse Casting Networks HTML. Selectors should be verified against live site."""
        soup = BeautifulSoup(html, "html.parser")
        listings: list[CastingListing] = []

        items = soup.select("[data-testid='casting-listing'], .casting-listing")
        for item in items:
            try:
                link = item.find("a")
                if not link:
                    continue
                href = link.get("href", "")
                url = href if href.startswith("http") else f"https://www.castingnetworks.com{href}"

                title_el = item.select_one(".listing-title")
                title = title_el.get_text(strip=True) if title_el else link.get_text(strip=True)
                if not title:
                    continue

                location_el = item.select_one(".listing-location")
                location = location_el.get_text(strip=True) if location_el else "Los Angeles, CA"

                union_el = item.select_one(".listing-union")
                union_status = union_el.get_text(strip=True) if union_el else "non-union"

                type_el = item.select_one(".listing-type")
                role_type = type_el.get_text(strip=True).lower() if type_el else "other"

                listings.append(CastingListing(
                    title=title,
                    source="casting_networks",
                    url=url,
                    posted_date=date.today(),
                    location=location,
                    union_status=union_status,
                    role_type=role_type,
                    description=title,
                    how_to_apply=f"Apply on Casting Networks: {url}",
                ))
            except Exception:
                logger.exception("Failed to parse Casting Networks listing")
                continue

        return listings

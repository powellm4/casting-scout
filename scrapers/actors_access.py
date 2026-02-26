# scrapers/actors_access.py
from __future__ import annotations

import logging
import os
from datetime import date

from bs4 import BeautifulSoup

from models import CastingListing
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

ACTORS_ACCESS_URL = "https://www.actorsaccess.com/projects"


class ActorsAccessScraper(BaseScraper):
    """Best-effort scraper for Actors Access. Requires login credentials."""

    @property
    def source_name(self) -> str:
        return "actors_access"

    def scrape(self) -> list[CastingListing]:
        email = os.environ.get("ACTORS_ACCESS_EMAIL", "")
        password = os.environ.get("ACTORS_ACCESS_PASSWORD", "")
        if not email or not password:
            logger.info("Actors Access credentials not configured, skipping")
            return []

        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Attempt login
                page.goto("https://www.actorsaccess.com/", wait_until="networkidle", timeout=60000)
                page.fill('input[name="email"], input[type="email"]', email)
                page.fill('input[name="password"], input[type="password"]', password)
                page.click('button[type="submit"], input[type="submit"]')
                page.wait_for_load_state("networkidle", timeout=30000)

                # Navigate to projects
                page.goto(ACTORS_ACCESS_URL, wait_until="networkidle", timeout=60000)
                html = page.content()
                browser.close()
                return self.parse_html(html)
        except Exception:
            logger.exception("Actors Access scraper failed")
            return []

    def parse_html(self, html: str) -> list[CastingListing]:
        """Parse Actors Access project listings. Selectors need live verification."""
        soup = BeautifulSoup(html, "html.parser")
        listings: list[CastingListing] = []

        # Actors Access uses various layouts; these are best-guess selectors
        projects = soup.select(".project-listing, .project-item, tr.project-row")
        for project in projects:
            try:
                link = project.find("a")
                if not link:
                    continue
                href = link.get("href", "")
                url = href if href.startswith("http") else f"https://www.actorsaccess.com{href}"
                title = link.get_text(strip=True)
                if not title:
                    continue

                listings.append(CastingListing(
                    title=title,
                    source="actors_access",
                    url=url,
                    posted_date=date.today(),
                    location="Los Angeles, CA",
                    union_status="non-union",
                    role_type="other",
                    description=title,
                    how_to_apply=f"Apply on Actors Access: {url}",
                ))
            except Exception:
                logger.exception("Failed to parse Actors Access project")
                continue

        return listings

# scrapers/craigslist.py
from __future__ import annotations

import logging
from datetime import date, datetime

import requests
from bs4 import BeautifulSoup

from models import CastingListing
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

CRAIGSLIST_URL = "https://losangeles.craigslist.org/search/tlg"


class CraigslistScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return "craigslist"

    def scrape(self) -> list[CastingListing]:
        try:
            resp = requests.get(CRAIGSLIST_URL, timeout=30, headers={
                "User-Agent": "Mozilla/5.0 (compatible; CastingScout/1.0)"
            })
            resp.raise_for_status()
            return self.parse_html(resp.text)
        except Exception:
            logger.exception("Craigslist scraper failed")
            return []

    def parse_html(self, html: str) -> list[CastingListing]:
        """Parse Craigslist talent gigs HTML into CastingListing objects."""
        soup = BeautifulSoup(html, "html.parser")
        listings: list[CastingListing] = []

        results = soup.select("li.cl-static-search-result")
        for item in results:
            try:
                link = item.find("a")
                if not link:
                    continue
                url = link.get("href", "")
                title_el = item.select_one(".title")
                title = title_el.get_text(strip=True) if title_el else item.get("title", "")
                if not title or not url:
                    continue

                location_el = item.select_one(".location")
                location = location_el.get_text(strip=True) if location_el else "Los Angeles"

                date_el = item.select_one(".date")
                posted = self._parse_date(date_el.get_text(strip=True)) if date_el else date.today()

                role_type = self._infer_role_type(title)
                school = self._detect_school(title)

                listings.append(CastingListing(
                    title=title,
                    source="craigslist",
                    url=url if url.startswith("http") else f"https://losangeles.craigslist.org{url}",
                    posted_date=posted,
                    location=location,
                    union_status="",  # Craigslist rarely specifies
                    role_type=role_type,
                    description=title,  # Full description requires visiting each post
                    how_to_apply=f"Reply on Craigslist: {url}",
                    school_or_production=school,
                ))
            except Exception:
                logger.exception("Failed to parse Craigslist listing")
                continue

        return listings

    def _parse_date(self, text: str) -> date:
        """Parse Craigslist date strings like 'Feb 25' or '2/25'."""
        try:
            current_year = date.today().year
            for fmt in ("%b %d", "%m/%d"):
                try:
                    parsed = datetime.strptime(text.strip(), fmt).replace(year=current_year)
                    return parsed.date()
                except ValueError:
                    continue
        except Exception:
            pass
        return date.today()

    def _infer_role_type(self, title: str) -> str:
        t = title.lower()
        if any(w in t for w in ("background", "extra", "extras", "bg")):
            return "background"
        if any(w in t for w in ("lead", "principal", "starring")):
            return "principal"
        if any(w in t for w in ("commercial", "spot", "ad ")):
            return "commercial"
        if any(w in t for w in ("voice", "vo ", "voiceover")):
            return "voice"
        return "other"

    def _detect_school(self, title: str) -> str | None:
        t = title.lower()
        schools = {"usc": "USC", "ucla": "UCLA", "afi": "AFI", "calarts": "CalArts",
                    "chapman": "Chapman", "lmu": "LMU", "loyola marymount": "LMU"}
        for key, name in schools.items():
            if key in t:
                return name
        if "student film" in t:
            return "Student Film"
        return None

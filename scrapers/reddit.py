# scrapers/reddit.py
from __future__ import annotations

import logging
import re
from datetime import date, datetime

import requests

from config import REDDIT_SUBREDDITS
from models import CastingListing
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class RedditScraper(BaseScraper):
    @property
    def source_name(self) -> str:
        return "reddit"

    def scrape(self) -> list[CastingListing]:
        all_listings: list[CastingListing] = []
        for sub in REDDIT_SUBREDDITS:
            try:
                url = f"https://www.reddit.com/r/{sub}/new.json?limit=50"
                resp = requests.get(url, timeout=30, headers={
                    "User-Agent": "CastingScout/1.0 (personal casting aggregator)"
                })
                resp.raise_for_status()
                all_listings.extend(self.parse_json(resp.json()))
            except Exception:
                logger.exception(f"Reddit scraper failed for r/{sub}")
        return all_listings

    def parse_json(self, data: dict) -> list[CastingListing]:
        listings: list[CastingListing] = []
        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})
            try:
                title = post.get("title", "")
                selftext = post.get("selftext", "")
                permalink = post.get("permalink", "")
                created = post.get("created_utc", 0)

                if not title:
                    continue

                url = f"https://www.reddit.com{permalink}" if permalink else post.get("url", "")
                posted_date = datetime.fromtimestamp(created).date() if created else date.today()
                location = self._extract_location(f"{title} {selftext}")
                role_type = self._infer_role_type(f"{title} {selftext}")
                school = self._detect_school(f"{title} {selftext}")

                listings.append(CastingListing(
                    title=self._clean_title(title),
                    source="reddit",
                    url=url,
                    posted_date=posted_date,
                    location=location,
                    union_status="",  # Reddit posts rarely specify
                    role_type=role_type,
                    description=selftext[:500] if selftext else title,
                    how_to_apply=f"See Reddit post: {url}",
                    school_or_production=school,
                ))
            except Exception:
                logger.exception("Failed to parse Reddit post")
                continue
        return listings

    def _clean_title(self, title: str) -> str:
        """Remove common Reddit prefixes like [CASTING], [HIRING], etc."""
        return re.sub(r"^\[.*?\]\s*", "", title).strip()

    def _extract_location(self, text: str) -> str:
        """Try to extract a location from text. Default to empty string."""
        t = text.lower()
        la_keywords = [
            "los angeles", "hollywood", "burbank", "santa monica",
            "studio city", "culver city", "downtown la", "glendale",
            "pasadena", "north hollywood", "van nuys",
        ]
        for kw in la_keywords:
            if kw in t:
                return kw.title() + ", CA"
        if " la " in t or t.startswith("la ") or t.endswith(" la"):
            return "Los Angeles, CA"
        return ""

    def _infer_role_type(self, text: str) -> str:
        t = text.lower()
        if any(w in t for w in ("background", "extra", "extras", "bg")):
            return "background"
        if any(w in t for w in ("lead", "principal", "starring")):
            return "principal"
        if any(w in t for w in ("commercial", "spot")):
            return "commercial"
        if any(w in t for w in ("voice", "vo ", "voiceover")):
            return "voice"
        return "other"

    def _detect_school(self, text: str) -> str | None:
        t = text.lower()
        schools = {"usc": "USC", "ucla": "UCLA", "afi": "AFI", "calarts": "CalArts",
                    "chapman": "Chapman", "lmu": "LMU"}
        for key, name in schools.items():
            if key in t:
                return name
        if "student film" in t:
            return "Student Film"
        return None

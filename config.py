# config.py
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

# --- Email ---
SENDGRID_API_KEY: str = os.environ.get("SENDGRID_API_KEY", "")
RECIPIENT_EMAIL: str = os.environ.get("RECIPIENT_EMAIL", "")
SENDER_EMAIL: str = os.environ.get("SENDER_EMAIL", "castingscout@noreply.com")

# --- Location filter ---
LA_METRO_LOCATIONS: list[str] = [
    "los angeles", "la", "burbank", "glendale", "pasadena",
    "santa monica", "hollywood", "west hollywood", "culver city",
    "studio city", "north hollywood", "sherman oaks", "van nuys",
    "long beach", "inglewood", "beverly hills", "century city",
    "downtown la", "koreatown", "silver lake", "echo park",
    "los feliz", "atwater village", "eagle rock", "highland park",
    "mar vista", "venice", "playa del rey", "westwood",
    "brentwood", "encino", "tarzana", "woodland hills",
    "calabasas", "malibu", "torrance", "redondo beach",
    "manhattan beach", "hermosa beach", "el segundo",
]

# --- Union filter ---
NON_UNION_KEYWORDS: list[str] = [
    "non-union", "nonunion", "non union", "open to all",
    "no union", "any union status",
]

# --- Freshness ---
FRESHNESS_HOURS: int = 48

# --- Scraper toggles ---
SCRAPERS_ENABLED: dict[str, bool] = {
    "backstage": True,
    "casting_networks": True,
    "craigslist": True,
    "actors_access": True,
    "reddit": True,
    "facebook": True,
}

# --- Reddit ---
REDDIT_SUBREDDITS: list[str] = ["actingjobs", "filmmakers"]

# --- Data ---
SEEN_LISTINGS_PATH: str = "data/seen_listings.json"

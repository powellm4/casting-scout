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
    "backstage": False,       # Needs live DOM selectors
    "casting_networks": False, # Needs live DOM selectors
    "craigslist": True,
    "actors_access": False,   # Requires login credentials
    "reddit": False,          # Blocked by Reddit (403)
    "facebook": False,        # Requires cookies
}

# --- Reddit ---
REDDIT_SUBREDDITS: list[str] = ["actingjobs", "filmmakers"]

# --- Profile filter (exclude listings that clearly don't match) ---
EXCLUDE_KEYWORDS: list[str] = [
    # Gender-specific (not male)
    "female", "females", "woman", "women", "girl", "girls", "ladies",
    "actress", "actresses", "latina", "she/her",
    "busty", "boudoir", "booth babe",
    "egg donor",
    # Race-specific (not white)
    "black male", "black female", "black actor", "black men",
    "african american", "afro-latina", "aapi", "asian model",
    "japanese-speaking", "japanese host",
    # Age ranges that don't fit
    "child actor", "ages 5", "ages 6", "ages 7", "ages 8", "ages 9",
    "youth participant", "15-18", "boys (ages",
    "65+", "60+", "70+", "elderly",
    # Not acting/performing
    "egg donor", "focus group", "research study", "data collection",
    "survey", "interview specialist", "cold caller",
    "tattoo assistant", "personal assistant",
    "hostess for karaoke", "ktv club", "booth helper",
    "sportsbook promoter", "intern wanted",
]

# --- Data ---
SEEN_LISTINGS_PATH: str = "data/seen_listings.json"

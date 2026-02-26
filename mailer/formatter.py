# mailer/formatter.py
from __future__ import annotations

from datetime import date
from itertools import groupby

from models import CastingListing, CareerCategory

CATEGORY_LABELS = {
    CareerCategory.PRINCIPAL: "Principal / Speaking Roles",
    CareerCategory.STUDENT_FILM: "Student Films (Top Schools)",
    CareerCategory.COMMERCIAL: "Commercials",
    CareerCategory.SHORT_INDIE: "Short Films & Indie Features",
    CareerCategory.BACKGROUND: "Background / Extra Work",
    CareerCategory.OPEN_CALL: "Open Calls & Workshops",
}

CATEGORY_DESCRIPTIONS = {
    CareerCategory.PRINCIPAL: "Builds your demo reel",
    CareerCategory.STUDENT_FILM: "Festival credits open doors",
    CareerCategory.COMMERCIAL: "Visibility + SAG vouchers",
    CareerCategory.SHORT_INDIE: "Resume credits & networking",
    CareerCategory.BACKGROUND: "Set experience + SAG vouchers",
    CareerCategory.OPEN_CALL: "Networking & practice",
}


def format_digest(
    listings: list[CastingListing],
    failed_sources: list[str] | None = None,
) -> tuple[str, str]:
    """Format listings into an email subject and HTML body.

    Returns:
        (subject, html_body)
    """
    today = date.today().strftime("%b %d")
    count = len(listings)

    if count == 0:
        subject = f"Casting Scout — No New Opportunities ({today})"
        html = _empty_template(today, failed_sources)
        return subject, html

    subject = f"Casting Scout — {count} New Opportunit{'y' if count == 1 else 'ies'} ({today})"

    # Sort and group by career category
    sorted_listings = sorted(listings, key=lambda l: l.categorize().value)
    grouped = {}
    for cat, group in groupby(sorted_listings, key=lambda l: l.categorize()):
        grouped[cat] = list(group)

    html = _build_html(today, count, grouped, failed_sources)
    return subject, html


def _empty_template(today: str, failed_sources: list[str] | None) -> str:
    fail_note = ""
    if failed_sources:
        fail_note = f"<p style='color:#888;'>Note: {', '.join(failed_sources)} were unavailable today.</p>"
    return f"""<html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
<h1 style="color: #333;">Casting Scout</h1>
<p>No new casting opportunities found today ({today}). Keep checking your direct sources!</p>
{fail_note}
</body></html>"""


def _build_html(
    today: str,
    count: int,
    grouped: dict[CareerCategory, list[CastingListing]],
    failed_sources: list[str] | None,
) -> str:
    sections = []
    listing_num = 0

    for cat in CareerCategory:
        if cat not in grouped:
            continue
        cat_listings = grouped[cat]
        label = CATEGORY_LABELS[cat]
        desc = CATEGORY_DESCRIPTIONS[cat]
        items = []
        for listing in cat_listings:
            listing_num += 1
            school_badge = ""
            if listing.school_or_production:
                school_badge = f" <span style='background:#4CAF50;color:white;padding:2px 6px;border-radius:3px;font-size:12px;'>{listing.school_or_production}</span>"

            comp = f"<br>Compensation: {listing.compensation}" if listing.compensation else ""
            deadline = f" | Deadline: {listing.deadline.strftime('%b %d')}" if listing.deadline else ""

            items.append(f"""
            <div style="margin-bottom: 16px; padding: 12px; background: #f9f9f9; border-radius: 8px;">
                <strong>{listing_num}. {listing.title}</strong>{school_badge}<br>
                Location: {listing.location} | Role: {listing.role_type.title()}{comp}<br>
                <span style="color:#666;">Source: {listing.source.title()}{deadline}</span><br>
                <span style="color:#444; font-size: 14px;">{listing.description[:200]}{'...' if len(listing.description) > 200 else ''}</span><br>
                <a href="{listing.url}" style="color:#1a73e8;">Apply / View Details</a>
            </div>""")

        sections.append(f"""
        <div style="margin-bottom: 24px;">
            <h2 style="color:#333; border-bottom: 2px solid #1a73e8; padding-bottom: 4px;">{label}</h2>
            <p style="color:#666; margin-top:0; font-size:14px;">{desc}</p>
            {''.join(items)}
        </div>""")

    fail_note = ""
    if failed_sources:
        fail_note = f"<p style='color:#888; font-size:13px;'>Unavailable today: {', '.join(failed_sources)}</p>"

    return f"""<html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
<h1 style="color: #333;">Casting Scout</h1>
<p style="color:#666;">{count} new opportunit{'y' if count == 1 else 'ies'} found — {today}</p>
<hr style="border: 1px solid #eee;">
{''.join(sections)}
{fail_note}
<hr style="border: 1px solid #eee;">
<p style="color:#999; font-size:12px;">Casting Scout — your daily LA casting digest</p>
</body></html>"""

# mailer/sender.py
from __future__ import annotations

import logging
import time

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logger = logging.getLogger(__name__)


def send_email(
    subject: str,
    html_body: str,
    api_key: str,
    to_email: str,
    from_email: str = "castingscout@noreply.com",
    retry: bool = True,
) -> bool:
    """Send an HTML email via SendGrid. Returns True on success."""
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_body,
    )
    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        logger.info(f"Email sent: status {response.status_code}")
        return True
    except Exception:
        logger.exception("Failed to send email")
        if retry:
            logger.info("Retrying in 5 minutes...")
            time.sleep(300)
            return send_email(subject, html_body, api_key, to_email, from_email, retry=False)
        return False

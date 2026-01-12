"""SMTP utility for sending emails."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def parse_smtp_url(smtp_url: str) -> dict[str, str | int | bool]:
    """Parse SMTP URL into connection components."""
    if not smtp_url:
        return {}

    # If no scheme, assume it's host:port format and add smtp:// prefix
    if "://" not in smtp_url:
        smtp_url = f"smtp://{smtp_url}"

    parsed = urlparse(smtp_url)
    scheme = parsed.scheme.lower() if parsed.scheme else "smtp"

    return {
        "host": parsed.hostname or "",
        "port": parsed.port or (587 if scheme == "smtp" else 465),
        "username": parsed.username or "",
        "password": parsed.password or "",
        "use_tls": scheme == "smtp",
    }


def send_email(
    smtp_url: str,
    to_email: str,
    to_name: str,
    from_email: str,
    from_name: str,
    subject: str,
    html_body: str | None = None,
    text_body: str | None = None,
) -> None:
    """Send email via SMTP."""
    smtp_config = parse_smtp_url(smtp_url)

    if not smtp_config or not smtp_config.get("host"):
        logger.error("[SMTP] Configuration missing or invalid")
        raise ValueError(
            f"[SMTP] Configuration missing or invalid: {smtp_config}"
        )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{from_email}>"
    msg["To"] = f"{to_name} <{to_email}>" if to_name else to_email

    if text_body:
        msg.attach(MIMEText(text_body, "plain", "utf-8"))
    if html_body:
        msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(smtp_config["host"], smtp_config["port"]) as server:
            server.send_message(msg)
    except Exception as e:
        logger.error(f"[SMTP] Failed to send email to {to_email}: {e}")
        raise

    logger.info(f"[SMTP] Sent to {to_email}")

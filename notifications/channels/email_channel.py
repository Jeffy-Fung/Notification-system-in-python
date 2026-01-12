import asyncio
import logging
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader

from ...core.config import get_settings
from .base_channel import BaseChannel
from ..utils.smtp_util import send_email
from ..notifications.base_notifications import Recipient
from ..loggers.s3_logger import S3Logger

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "email"
ASSETS_DIR = TEMPLATE_DIR / "assets"
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


def read_svg(filename: str) -> str:
    """Read SVG file and return as string for inlining."""
    svg_path = ASSETS_DIR / filename
    if svg_path.exists():
        return svg_path.read_text()
    return ""


# Make read_svg available in templates
jinja_env.globals["read_svg"] = read_svg


class EmailChannel(BaseChannel):

    @classmethod
    def get_loggers(cls) -> list[type]:
        """Get loggers for email channel."""
        return [S3Logger]

    @staticmethod
    def _validate_required_args(**kwargs) -> None:
        """Validate required arguments for email channel."""
        if "template" not in kwargs:
            raise ValueError("'template' is required for email channel")
        if "template_vars" not in kwargs:
            raise ValueError("'template_vars' is required for email channel")

        template = kwargs["template"]
        if "subject" not in template:
            raise ValueError("'subject' is required in template")

    @classmethod
    async def _send_message(cls, recipient: Recipient, **kwargs) -> None:
        """Send email via SMTP."""
        cls._validate_required_args(**kwargs)

        template = kwargs["template"]
        template_vars = kwargs["template_vars"]
        subject = template["subject"]

        html_body, text_body = cls._render_body_templates(
            template, template_vars
        )

        if not html_body and not text_body:
            logger.warning(
                f"[Email] No body content for email to {recipient.email}"
            )
            return

        from_email, from_name = cls._get_sender_info(template_vars)

        await asyncio.to_thread(
            send_email,
            get_settings().smtp_url,
            recipient.email,
            recipient.name,
            from_email,
            from_name,
            subject,
            html_body,
            text_body,
        )

    @classmethod
    def _prepare_log_data(
        cls,
        recipient: Recipient,
        **kwargs,
    ) -> Dict[str, Any]:
        log_data = super()._prepare_log_data(recipient, **kwargs)

        template = kwargs.get("template", {})
        template_vars = kwargs.get("template_vars", {})

        html_body, text_body = cls._render_body_templates(
            template, template_vars
        )

        log_data.update(
            {
                "template_vars": template_vars,
                "html_body": html_body,
                "text_body": text_body,
            }
        )

        if template.get("subject"):
            log_data["subject"] = template["subject"]

        return log_data

    @staticmethod
    def _render_template(template_name: str, template_vars: dict) -> str:
        """Render template file with variables."""
        try:
            template = jinja_env.get_template(template_name)
            return template.render(**template_vars)
        except Exception as e:
            logger.error(
                f"[Email] Failed to render template {template_name}: {e}"
            )
            raise

    @staticmethod
    def _render_body_templates(
        template: dict, template_vars: dict
    ) -> tuple[str | None, str | None]:
        """Render HTML and text body templates."""
        html_body = (
            EmailChannel._render_template(template["html"], template_vars)
            if template.get("html")
            else None
        )
        text_body = (
            EmailChannel._render_template(template["text"], template_vars)
            if template.get("text")
            else None
        )
        return html_body, text_body

    @staticmethod
    def _get_sender_info(template_vars: dict) -> tuple[str, str]:
        """Get sender email and name from template vars or defaults."""
        from_email = template_vars.get("from_email", "no-reply@example.com")
        from_name = template_vars.get("from_name", "Example No Reply")
        return from_email, from_name

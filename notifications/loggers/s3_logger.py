import asyncio
import logging
from typing import Any

from .base_logger import BaseLogger
from ..utils.s3_handler import upload_log_to_s3
from ...core.config import get_settings

logger = logging.getLogger(__name__)


class S3Logger(BaseLogger):
    """Logger that uploads notification logs to S3."""

    @classmethod
    async def log(cls, log_data: dict[str, Any]) -> None:
        """Upload log data to S3 asynchronously.

        Args:
            log_data: Dictionary containing log information
        """
        try:
            log_type = log_data.get("channel", "unknown")
            settings = get_settings()

            await asyncio.to_thread(
                upload_log_to_s3,
                log_data,
                log_type,
                settings.aws_s3_email_log_bucket,
            )

        except Exception as e:
            # Don't let logging failures affect the main flow
            logger.error(f"[S3Logger] Failed to log to S3: {e}")

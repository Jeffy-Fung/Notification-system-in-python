import json
import logging
import uuid
from datetime import datetime
from typing import Any

import boto3
from botocore.exceptions import ClientError

from ...core.config import get_settings

logger = logging.getLogger(__name__)


def upload_log_to_s3(
    log_data: dict[str, Any], log_type: str, bucket: str
) -> None:
    """Upload log data to S3.

    Args:
        log_data: Dictionary containing log information
        log_type: Type of log (e.g., 'email', 'sms')
        bucket: S3 bucket name

    Returns:
        True if upload successful, False otherwise
    """
    try:
        settings = get_settings()

        client = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )

        timestamp = datetime.now()
        year = timestamp.strftime("%Y")
        month = timestamp.strftime("%m")
        day = timestamp.strftime("%d")
        hour = timestamp.strftime("%H")

        # Partitioned path structure
        date_path = f"year={year}/month={month}/day={day}/hour={hour}"

        # Filename with timestamp and short UUID
        uuid_short = str(uuid.uuid4())[:8]
        file_name = f"{timestamp.isoformat()}_{uuid_short}.json"
        file_key = f"{log_type}/{date_path}/{file_name}"

        client.put_object(
            Bucket=bucket,
            Key=file_key,
            Body=json.dumps(log_data, indent=2, default=str),
            ContentType="application/json",
        )

        logger.info(f"[S3] Uploaded log to s3://{bucket}/{file_key}")

    except ClientError as e:
        logger.error(f"[S3] Failed to upload log: {e}")
    except Exception as e:
        logger.error(f"[S3] Unexpected error uploading log: {e}")

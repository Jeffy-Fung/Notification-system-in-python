import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..channels.base_channel import BaseChannel

logger = logging.getLogger(__name__)

@dataclass
class Recipient:
    """Recipient information for notifications."""

    name: str
    email: str


@dataclass
class NotificationResult:
    """Result of sending a notification."""

    notification_type: str
    recipient: dict[str, str]
    channels: dict[str, dict[str, Any]]
    parameters: dict[str, Any] = field(default_factory=dict)


class BaseNotification(ABC):
    """Base notification"""

    @classmethod
    @abstractmethod
    def get_channels(cls) -> list[type[BaseChannel]]:
        """Get list of channel classes to use."""
        raise NotImplementedError

    @classmethod
    async def send(cls, recipient: Recipient, **kwargs) -> NotificationResult:
        """Send notification via all channels.

        Returns:
            NotificationResult: Complete notification response with channel statuses
        """
        payloads = cls.prepare_payloads(recipient, **kwargs)
        cls._add_metadata_to_payloads(payloads, recipient, **kwargs)

        tasks, channel_classes = cls._create_channel_tasks(recipient, payloads)
        results = await asyncio.gather(*tasks, return_exceptions=True)

        channel_results = cls._process_channel_results(
            channel_classes, results
        )

        return NotificationResult(
            notification_type=cls.__name__,
            recipient=cls._format_recipient_info(recipient),
            channels=channel_results,
            parameters=kwargs,
        )

    @classmethod
    def _create_channel_tasks(
        cls, recipient: Recipient, payloads: dict[str, dict]
    ) -> tuple[list, list[type[BaseChannel]]]:
        """Create async tasks for each available channel."""
        tasks = []
        channel_classes = []
        channels = cls.get_channels()

        for channel_class in channels:
            channel_name = channel_class.get_name()
            if channel_name not in payloads:
                continue

            task = cls._send_with_channel(
                channel_class, recipient, payloads[channel_name]
            )
            tasks.append(task)
            channel_classes.append(channel_class)

        return tasks, channel_classes

    @classmethod
    def _process_channel_results(
        cls,
        channel_classes: list[type[BaseChannel]],
        results: list,
    ) -> dict[str, dict[str, Any]]:
        """Process channel results and build status dictionary."""
        channel_results = {}

        for channel_class, result in zip(channel_classes, results):
            channel_name = channel_class.get_name()

            if isinstance(result, Exception):
                channel_results[channel_name] = {
                    "success": False,
                    "error": str(result),
                    "channel_class": channel_class,
                }
                logger.error(
                    f"[{cls.__name__}] {channel_name} failed: {result}"
                )
            else:
                channel_results[channel_name] = {
                    "success": True,
                    "channel_class": channel_class,
                    "channel_result": result,
                }

        return channel_results

    @staticmethod
    def _format_recipient_info(recipient: Recipient) -> dict[str, str]:
        """Format recipient information for response."""
        return {
            "name": recipient.name,
            "email": recipient.email,
        }

    @classmethod
    def send_background(
        cls, background_tasks, recipient: Recipient, **kwargs
    ) -> None:
        """Schedule notification to send in background."""
        raise NotImplementedError("TODO: Not implemented yet")

    @classmethod
    @abstractmethod
    def prepare_payloads(
        cls, recipient: Recipient, **kwargs
    ) -> dict[str, dict]:
        """Prepare payloads for each channel."""
        raise NotImplementedError

    @classmethod
    def _add_metadata_to_payloads(
        cls, payloads: dict[str, dict], recipient: Recipient, **kwargs
    ) -> None:
        """Add common metadata to all payloads."""
        for payload in payloads.values():
            payload.update(
                {
                    "notification_type": cls.__name__,
                    "metadata": {
                        **kwargs.get("metadata", {}),
                    },
                }
            )

    @classmethod
    async def _send_with_channel(
        cls,
        channel_class: type[BaseChannel],
        recipient: Recipient,
        payload: dict,
    ) -> dict[str, Any]:
        """Helper for concurrent sending via channel."""
        return await channel_class.send(recipient, **payload)

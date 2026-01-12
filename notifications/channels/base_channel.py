from abc import ABC, abstractmethod
from typing import Any, Dict
from ..notifications.base_notifications import Recipient


class BaseChannel(ABC):
    """Base Channel with simple logging"""

    @classmethod
    def get_loggers(cls) -> list[type]:
        """Get list of logger classes to use. Override in subclasses."""
        return []

    @classmethod
    async def send(cls, recipient: Recipient, **kwargs) -> Dict[str, Any]:
        """Send notification with logging"""
        log_data = cls._prepare_log_data(recipient, **kwargs)

        await cls._send_message(recipient, **kwargs)
        await cls._log_to_all_loggers(log_data)

        return log_data

    @classmethod
    async def _log_to_all_loggers(cls, log_data: Dict[str, Any]) -> None:
        """Log to all configured loggers."""
        loggers = cls.get_loggers()
        for logger_class in loggers:
            try:
                await logger_class.log(log_data)
            except Exception:
                # Don't let logging failures affect the main flow
                pass

    @classmethod
    @abstractmethod
    async def _send_message(cls, recipient: Recipient, **kwargs) -> None:
        """Actual sending logic - implemented by subclasses"""
        raise NotImplementedError

    @classmethod
    def _prepare_log_data(
        cls, recipient: Recipient, **kwargs
    ) -> Dict[str, Any]:
        """Prepare log data - can be overridden by subclasses"""
        return {
            "recipient": {
                "email": recipient.email,
                "name": recipient.name,
            },
            "notification_type": kwargs.get("notification_type", "unknown"),
            "template": kwargs.get("template"),
            "metadata": kwargs.get("metadata", {}),
        }

    @classmethod
    def get_name(cls) -> str:
        """Get channel name from class name."""
        return cls.__name__.lower().replace("channel", "")

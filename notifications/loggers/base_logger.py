from abc import ABC, abstractmethod
from typing import Any


class BaseLogger(ABC):
    """Base class for notification loggers."""

    @classmethod
    @abstractmethod
    async def log(cls, log_data: dict[str, Any]) -> None:
        """Log notification data.

        Args:
            log_data: Dictionary containing log information
        """
        raise NotImplementedError

    @classmethod
    def get_name(cls) -> str:
        """Get logger name from class name."""
        return cls.__name__.lower().replace("logger", "")

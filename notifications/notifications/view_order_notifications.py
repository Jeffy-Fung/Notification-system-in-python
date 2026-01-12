from ..channels.email_channel import EmailChannel
from ..channels.base_channel import BaseChannel
from .base_notifications import BaseNotification, NotificationResult, Recipient


class ViewOrderNotification(BaseNotification):
    """Notification for viewing order details."""

    @classmethod
    def get_channels(cls) -> list[type[BaseChannel]]:
        """Get channels for this notification."""
        return [EmailChannel]

    @classmethod
    async def send(
        cls,
        recipient: Recipient,
        date: str,
        time: str,
        prompt: str,
        timestamp: str,
        query_over_limit: bool,
    ) -> NotificationResult:
        """Send view order notification with specific parameters."""
        return await super().send(
            recipient,
            date=date,
            time=time,
            prompt=prompt,
            timestamp=timestamp,
            query_over_limit=query_over_limit,
        )

    @classmethod
    def prepare_payloads(
        cls, recipient: Recipient, **kwargs
    ) -> dict[str, dict]:
        """Prepare payloads for each channel."""
        return {
            "email": {
                "template": {
                    "subject": "View Order Details",
                    "html": "view_order.html",
                    "text": "view_order.txt",
                },
                "template_vars": {
                    "name": recipient.name,
                    "date": kwargs.get("date", ""),
                    "time": kwargs.get("time", ""),
                    "timestamp": kwargs.get("timestamp", ""),
                    "support_email": "example@example.com",
                },
            },
        }

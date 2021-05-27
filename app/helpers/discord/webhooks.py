import logging
from requests.exceptions import Timeout
from discord_webhook import DiscordWebhook

logger = logging.getLogger('discord_webhook')

class CustomDiscordWebhook(DiscordWebhook):
    def __init__(self, url=None, **kwargs):
        super().__init__(url, **kwargs)

    @property
    def is_enabled(self) -> bool:
        """Checks if Discord webhook is enabled."""
        return self.url is not None and len(self.url) > 0

    def send(self) -> None:
        """Executes the webhook and handles Timeout exception"""
        if self.is_enabled is False:
            return None

        try:
            self.execute(remove_embeds=True)
        except Timeout as e:
            logger.error('requests.exceptions.Timeout exception has occurred: {} - {}'.format(
                e.request.method,
                e.request.url
            ))
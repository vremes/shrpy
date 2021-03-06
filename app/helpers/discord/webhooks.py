import logging
from requests.exceptions import Timeout
from discord_webhook import DiscordWebhook
from app.helpers.discord.embeds import EmbedType, FileEmbed, ShortUrlEmbed

logger = logging.getLogger('discord_webhook')

class CustomDiscordWebhook(DiscordWebhook):
    def __init__(self, url=None, **kwargs):
        super().__init__(url, **kwargs)

    @property
    def is_enabled(self) -> bool:
        """Checks if Discord webhook is enabled."""
        return self.url is not None and len(self.url) > 0

    def embed(self, embed_type = EmbedType.FILE, **kwargs):
        """Creates embed instance based on `embed_type` using given arguments and adds it to webhook."""
        if embed_type == EmbedType.FILE:
            embed = FileEmbed(**kwargs)
        elif embed_type == EmbedType.SHORT_URL:
            embed = ShortUrlEmbed(**kwargs)

        # Add embed to webhook
        self.add_embed(embed)

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
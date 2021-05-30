# standard library imports
import logging
from random import randint

# pip imports
from requests.exceptions import Timeout
from discord_webhook import DiscordWebhook, DiscordEmbed

# local imports
from app.helpers.utils import Message

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

class CustomDiscordEmbed(DiscordEmbed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # ShareX file URL/short URL and deletion URL
        self.content_url = kwargs.get('content_url')
        self.deletion_url = kwargs.get('deletion_url')

        # Add markdown links to embed
        self.add_embed_field(name=Message.URL, value=f'**[{Message.CLICK_HERE_TO_VIEW}]({self.content_url})**')
        self.add_embed_field(name=Message.DELETION_URL, value=f'**[{Message.CLICK_HERE_TO_DELETE}]({self.deletion_url})**')

        # Set random color for embed
        self.set_color(
            randint(0, 0xffffff)
        )

        self.set_timestamp()

class FileEmbed(CustomDiscordEmbed):
    def __init__(self, **kwargs):
        """Represents DiscordEmbed for files."""
        super().__init__(**kwargs)

        self.set_title(Message.FILE_UPLOADED)
        self.set_description(self.content_url)
        self.set_image(url=self.content_url)

class ShortUrlEmbed(CustomDiscordEmbed):
    def __init__(self, **kwargs):
        """Represents DiscordEmbed for short URLs."""
        super().__init__(**kwargs)

        self.set_title(Message.URL_SHORTENED)
        self.set_description('{} => {}'.format(
            kwargs.get('original_url'),
            kwargs.get('shortened_url')
        ))

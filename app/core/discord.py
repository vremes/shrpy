# standard library imports
from random import randint
from functools import cached_property

# pip imports
from flask import current_app
from requests.exceptions import Timeout
from discord_webhook import DiscordWebhook, DiscordEmbed

class CustomDiscordWebhook(DiscordWebhook):
    def __init__(self, url=None, **kwargs):
        super().__init__(url, **kwargs)

    @cached_property
    def is_enabled(self) -> bool:
        """Checks if Discord webhook is enabled."""
        return self.url is not None and len(self.url) > 0

    def execute(self, remove_embeds=True, remove_files=True):
        """Executes the webhook and handles Timeout exception."""
        if self.is_enabled is False:
            return None

        try:
            return super().execute(remove_embeds, remove_files)
        except Timeout as err:
            current_app.logger.error(f'requests.exceptions.Timeout exception has occurred during webhook execution: {err}')

class CustomDiscordEmbed(DiscordEmbed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # ShareX file URL/short URL and deletion URL
        self.content_url = kwargs.get('content_url')
        self.deletion_url = kwargs.get('deletion_url')

        # Add markdown links to embed
        self.add_embed_field(name='URL', value=f'**[Click here to view]({self.content_url})**')
        self.add_embed_field(name='Deletion URL', value=f'**[Click here to delete]({self.deletion_url})**')

        # Set random color for embed
        self.set_color(
            randint(0, 0xffffff)
        )

        self.set_timestamp()

class FileEmbed(CustomDiscordEmbed):
    def __init__(self, **kwargs):
        """Represents DiscordEmbed for files."""
        super().__init__(**kwargs)

        self.set_title('New file has been uploaded!')
        self.set_description(self.content_url)
        self.set_image(url=self.content_url)

class ShortUrlEmbed(CustomDiscordEmbed):
    def __init__(self, **kwargs):
        """Represents DiscordEmbed for short URLs."""
        super().__init__(**kwargs)

        self.set_title('URL has been shortened!')
        self.set_description('{} => {}'.format(
            kwargs.get('original_url'),
            kwargs.get('shortened_url')
        ))

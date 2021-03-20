from enum import Enum
from app.helpers.utils import random_hex
from discord_webhook import DiscordEmbed, DiscordWebhook

class EmbedType(Enum):
    FILE = 0
    SHORT_URL = 1

class CustomDiscordWebhook(DiscordWebhook):
    def __init__(self, url=None):
        super().__init__(url)

    @property
    def is_enabled(self) -> bool:
        """Checks if Discord webhook is enabled."""
        return self.url is not None and len(self.url) > 0

    def embed(self, title: str, description: str, url: str, deletion_url: str, is_file=False):
        """Creates DiscordEmbed instance using given arguments and adds it to webhook."""
        # Discord embed instance
        embed = DiscordEmbed()

        # Set title and description
        embed.set_title(title)
        embed.set_description(description)

        # Markdown links
        file_link = '**[Click here to view]({})**'.format(url)
        deletion_link = '**[Click here to delete]({})**'.format(deletion_url)

        # Add URL and deletion URL fields
        embed.add_embed_field(name='URL', value=file_link)
        embed.add_embed_field(name='Deletion URL', value=deletion_link)

        # Set random color
        embed.set_color(
            random_hex()
        )

        # Add image to embed if url is image
        if is_file and url.endswith(('.mp4', '.webm')) is False:
            embed.set_image(url=url)

        # Add timestamp to embed
        embed.set_timestamp()

        # Add embed to webhook
        self.add_embed(embed)

    def send(self, url: str, delete_url: str, embed_type: int = EmbedType.FILE, **kwargs) -> None:
        """Creates DiscordEmbed instance and sends it to the webhook"""
        if self.is_enabled is False:
            return None

        if embed_type == EmbedType.FILE:
            title = 'New file has been uploaded!'
            description = url
        elif embed_type == EmbedType.SHORT_URL:
            title = 'URL has been shortened!'
            description = '{} => {}'.format(
                kwargs.get('original_url'),
                kwargs.get('shortened_url')
            )

        self.embed(
            title=title,
            description=description,
            url=url,
            deletion_url=delete_url,
            is_file=embed_type == EmbedType.FILE
        )

        self.execute(remove_embeds=True)
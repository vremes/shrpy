from enum import IntEnum
from app.helpers.utils import random_hex
from discord_webhook import DiscordEmbed

class EmbedType(IntEnum):
    FILE = 0
    SHORT_URL = 1

class CustomDiscordEmbed(DiscordEmbed):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # ShareX file URL and deletion URL
        self.file_url = kwargs.get('file_url')
        self.delete_url = kwargs.get('delete_url')

        # Add markdown links to embed
        self.add_embed_field(name='URL', value='**[Click here to view]({})**'.format(self.file_url))
        self.add_embed_field(name='Deletion URL', value='**[Click here to delete]({})**'.format(self.delete_url))

        # Set random color for embed
        self.set_color(
            random_hex()
        )

        self.set_timestamp()

class FileEmbed(CustomDiscordEmbed):
    def __init__(self, **kwargs):
        """Represents DiscordEmbed for files."""
        super().__init__(**kwargs)
        self.set_title('New file has been uploaded!')
        self.set_description(self.file_url)
        self.set_image(url=self.file_url)

class ShortUrlEmbed(CustomDiscordEmbed):
    def __init__(self, **kwargs):
        """Represents DiscordEmbed for short URLs."""
        super().__init__(**kwargs)
        self.set_title('URL has been shortened!')
        self.set_description('{} => {}'.format(
            kwargs.get('original_url'),
            kwargs.get('shortened_url')
        ))

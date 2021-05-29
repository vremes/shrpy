from random import randint
from app.helpers.utils import Message
from discord_webhook import DiscordEmbed

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

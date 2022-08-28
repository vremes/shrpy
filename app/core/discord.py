# standard library imports
from random import randint

# pip imports
from requests.exceptions import Timeout
from discord_webhook import DiscordWebhook, DiscordEmbed

# local imports
import app

class CustomDiscordWebhook(DiscordWebhook):
    def __init__(self, url=None, **kwargs):
        super().__init__(url, **kwargs)

    @property
    def is_enabled(self) -> bool:
        """Checks if Discord webhook is enabled."""
        return self.url is not None and len(self.url) > 0

    def send_embed(self, embed: DiscordEmbed):
        """Sends the given DiscordEmbed to webhook."""
        if self.is_enabled is False:
            return

        self.add_embed(embed)

        try:
            return self.execute(True, True)
        except Timeout as err:
            app.logger.error(f'requests.exceptions.Timeout exception has occurred during webhook execution: {err}')

def create_uploaded_file_embed(url: str, deletion_url: str) -> DiscordEmbed:
    """Creates an instance of DiscordEmbed for uploaded files."""
    embed = DiscordEmbed()
    embed.set_title('New file has been uploaded!')
    embed.set_description(url)
    embed.set_image(url=url)
    embed.set_timestamp()
    embed.set_color(randint(0, 0xffffff))
    embed.add_embed_field(name='URL', value=f'**[Click here to view]({url})**')
    embed.add_embed_field(name='Deletion URL', value=f'**[Click here to delete]({deletion_url})**')
    return embed

def create_short_url_embed(original_url: str, shortened_url: str, deletion_url: str) -> DiscordEmbed:
    """Creates an instance of DiscordEmbed for shortened URLs."""
    embed = DiscordEmbed()
    embed.set_title('URL has been shortened!')
    embed.set_description('{} => {}'.format(original_url, shortened_url))
    embed.add_embed_field(name='URL', value=f'**[Click here to view]({original_url})**')
    embed.add_embed_field(name='Deletion URL', value=f'**[Click here to delete]({deletion_url})**')
    embed.set_color(randint(0, 0xffffff))
    embed.set_timestamp()
    return embed

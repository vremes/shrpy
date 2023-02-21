# standard library imports
from random import randint

# pip imports
from requests.exceptions import Timeout
from discord_webhook import DiscordWebhook, DiscordEmbed

def create_discord_webhooks(urls: list[str], timeout: float = 5.0) -> tuple[DiscordWebhook, ...]:
    """Creates a tuple of DiscordWebhook instances."""
    filtered_urls = [url for url in urls if url.strip()]
    return DiscordWebhook.create_batch(filtered_urls, timeout=timeout)

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

def execute_webhooks_with_embed(webhook_urls: tuple[DiscordWebhook, ...], embed: DiscordEmbed):
    """Executes a list of webhooks with given embed."""
    for webhook in webhook_urls:
        try:
            webhook.add_embed(embed)
            webhook.execute()
        except Timeout:
            break

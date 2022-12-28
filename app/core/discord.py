# standard library imports
from random import randint

# pip imports
from discord_webhook import DiscordWebhook, DiscordEmbed

def create_discord_webhooks(urls: list, timeout: float = 5.0) -> list[DiscordWebhook]:
    """Creates a list of CustomDiscordWebhook instances."""
    webhooks = []
    for url in urls:
        if not url:
            continue
        webhooks.append(DiscordWebhook(url, timeout=timeout))
    return webhooks

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

from discord_webhook import DiscordEmbed, DiscordWebhook

class CustomDiscordWebhook(DiscordWebhook):
    def __init__(self, app=None):
        """Custom Discord Webhook class which is initialised using Flask application"""
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        urls = app.config.get('DISCORD_WEBHOOKS')
        super().__init__(url=urls)

    def is_enabled(self) -> bool:
        """Checks if Discord webhook is enabled."""
        if self.url is None:
            return False
        return len(self.url) > 0

    def embed(self, title: str, description: str, url: str, deletion_url: str, is_file=False) -> DiscordEmbed:
        """Creates and returns DiscordEmbed instance using given arguments."""
        # Discord embed instance
        embed = DiscordEmbed()

        # Set title and description
        embed.set_title(title)
        embed.set_description(description)

        # Add URL and deletion URL fields
        embed.add_embed_field(name='URL', value=url)
        embed.add_embed_field(name='Deletion URL', value=deletion_url)

        # Add image/video to embed
        if is_file:
            embed.set_image(url=url)
            embed.set_video(url=url)

        # Add timestamp to embed
        embed.set_timestamp()

        return embed
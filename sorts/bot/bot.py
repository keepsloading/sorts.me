import os
import logging
import nextcord
from nextcord.ext import commands

from sorts.config import settings
from sorts.bot.utils import create_sortling_embed

logger = logging.getLogger(__name__)

ALLOWED_CHANNEL_ID = 1475575132108882133


class SortlingBot(commands.Bot):
    def __init__(self):
        intents = nextcord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def on_ready(self):
        logger.info(f"Bot connected as: {self.user.name} (ID: {self.user.id})")
        logger.info("Syncing slash commands globally...")
        activity = nextcord.Activity(type=nextcord.ActivityType.listening, name="/sort")
        await self.change_presence(activity=activity)
        logger.info("Ready to guide students!")

    async def check_application_command(self, interaction: nextcord.Interaction) -> bool:
        # Always allow admin command anywhere for setup/maintenance
        if interaction.application_command and interaction.application_command.name == "admin":
            return True

        allowed_channel_id = int(os.getenv("SORTLING_ALLOWED_CHANNEL_ID", str(ALLOWED_CHANNEL_ID)))

        # Enforce dedicated channel restriction if triggered in a different channel
        if interaction.channel_id and interaction.channel_id != allowed_channel_id:
            embed, file = create_sortling_embed(
                title="Wrong Channel 📍",
                description=f"Please use <#{allowed_channel_id}> to run Sortling commands!",
                is_error=False,
            )
            try:
                if file:
                    await interaction.response.send_message(embed=embed, file=file, ephemeral=True)
                else:
                    await interaction.response.send_message(embed=embed, ephemeral=True)
            except Exception:
                pass
            return False

        return True


def run_bot():
    """Bootstraps and executes the Nextcord Bot client."""
    if not settings.DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN is missing! Please configure it in your environment/.env file.")
        print("Error: DISCORD_TOKEN is missing. Please set it in your .env file.")
        return

    bot = SortlingBot()

    # Load all Cogs
    extensions = [
        "sorts.bot.cogs.about",
        "sorts.bot.cogs.clubs",
        "sorts.bot.cogs.feedback",
        "sorts.bot.cogs.sort",
        "sorts.bot.cogs.admin"
    ]

    for ext in extensions:
        try:
            bot.load_extension(ext)
            logger.info(f"Loaded extension: {ext}")
        except Exception as e:
            logger.exception(f"Failed to load extension {ext}: {str(e)}")

    bot.run(settings.DISCORD_TOKEN)

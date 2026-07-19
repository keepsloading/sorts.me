import nextcord
from nextcord.ext import commands
import logging
from sorts.config import settings

logger = logging.getLogger(__name__)

class SortlingBot(commands.Bot):
    def __init__(self):
        # Configure Discord intents
        intents = nextcord.Intents.default()
        intents.message_content = True  # Enable reading messages if needed
        
        super().__init__(
            command_prefix="!",  # We only support Slash commands, prefix is fallback
            intents=intents,
            help_command=None
        )

    async def on_ready(self):
        logger.info(f"Bot connected as: {self.user.name} (ID: {self.user.id})")
        logger.info("Syncing slash commands globally...")
        # Status
        activity = nextcord.Activity(type=nextcord.ActivityType.listening, name="/sort")
        await self.change_presence(activity=activity)
        logger.info("Ready to guide students!")

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

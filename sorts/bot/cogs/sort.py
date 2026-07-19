import os
import nextcord
from nextcord.ext import commands
from sorts.database.connection import get_db
from sorts.database import models as db_models
from sorts.services.session_service import SessionService
from sorts.bot.views.questionnaire import QuestionnaireView
from sorts.bot.utils import BRAND_COLOR, create_sortling_embed, get_guild_university

class SortCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session_service = SessionService()

    @nextcord.slash_command(name="sort", description="Start your interactive campus club recommendation questionnaire.")
    async def sort(self, interaction: nextcord.Interaction):
        """Starts a recommendation session and sends the first question embed with buttons."""
        user_id = str(interaction.user.id)
        
        with get_db() as db:
            # Retrieve university for this guild
            univ = get_guild_university(db, interaction.guild_id)
            if not univ:
                embed, file = create_sortling_embed(
                    title="Setup Required",
                    description=(
                        "Sortling: 'Hmm... This server hasn't been set up yet. "
                        "Please ask an administrator to run `/setup` to link this server to a university profile!'"
                    ),
                    color=BRAND_COLOR,
                    is_error=True
                )
                await interaction.send(embed=embed, file=file, ephemeral=True)
                return

            # Initialize a new session for this user
            session = self.session_service.create_session(db, univ.id, user_identifier=user_id)
            
            # Fetch the first question
            first_q = self.session_service.get_next_question(db, session.id)
            if not first_q:
                embed, file = create_sortling_embed(
                    title="No Questions Available",
                    description="Sortling: 'Hmm... I don't have any questions ready for this university. Let's add some!'",
                    color=BRAND_COLOR,
                    is_error=True
                )
                await interaction.send(embed=embed, file=file, ephemeral=True)
                return

            # Instantiate questionnaire buttons view
            view = QuestionnaireView(session.id, first_q)
            
            # Make the question card embed with Mascot thinking GIF
            embed = nextcord.Embed(
                title="Sortling's Questionnaire: Question 1",
                description=f"### {first_q.text}",
                color=BRAND_COLOR
            )
            embed.set_footer(text="Sortling: 'Answer honestly, and I'll find where you fit.'")

            # Attach thinking.gif
            file = None
            thinking_path = os.path.join("Sortling Mascot", "thinking.gif")
            if os.path.exists(thinking_path):
                file = nextcord.File(thinking_path, filename="thinking.gif")
                embed.set_thumbnail(url="attachment://thinking.gif")

            if file:
                await interaction.send(embed=embed, view=view, file=file, ephemeral=True)
            else:
                await interaction.send(embed=embed, view=view, ephemeral=True)

def setup(bot):
    bot.add_cog(SortCog(bot))

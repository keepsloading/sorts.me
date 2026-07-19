import nextcord
from nextcord.ext import commands
from sorts.database.connection import get_db
from sorts.database import models as db_models
from sorts.bot.utils import create_sortling_embed, BRAND_COLOR, get_guild_university, clean_text

class AboutCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="about", description="Learn about sorts.me and the campus guide Sortling.")
    async def about(self, interaction: nextcord.Interaction):
        """Displays university details and explains Sortling's guide philosophy."""
        with get_db() as db:
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

            # Create standard mascot embed
            embed, file = create_sortling_embed(
                title=f"Sortling: Campus Guide for {univ.name}",
                description=univ.description or "Your campus companion.",
                color=BRAND_COLOR,
                is_error=False
            )

            # If there's a custom university logo, set that as thumbnail instead, and place Mascot in author
            if univ.logo:
                embed.set_thumbnail(url=univ.logo)
                if file:
                    embed.set_author(name="sorts.me", icon_url="attachment://Icon_Neutral.png")
            
            embed.add_field(
                name="Who is Sortling?",
                value=clean_text(
                    "Sortling is a knowledgeable senior character who knows the campus inside out. "
                    "By asking a few adaptive questions, Sortling identifies your skills, workload availability, and social preferences "
                    "to match you with the perfect student groups. No generic chatbots, no AI hallucinations, just deterministic guidance."
                ),
                inline=False
            )
            embed.add_field(
                name="How do I get recommended?",
                value="Simply type `/sort` to start your adaptive guide questionnaire session!",
                inline=False
            )
            embed.add_field(
                name="Official Website",
                value=f"[Visit {univ.name}]({univ.website})",
                inline=True
            )

            embed.set_footer(text="sorts.me V1: Built for Extensibility")
            
            if file:
                await interaction.send(embed=embed, file=file)
            else:
                await interaction.send(embed=embed)

def setup(bot):
    bot.add_cog(AboutCog(bot))

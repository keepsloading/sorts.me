import nextcord
from nextcord.ext import commands
from sorts.database.connection import get_db
from sorts.services.club_service import ClubService
from sorts.database import models as db_models
from sorts.bot.views.club_list import ClubPagingView
from sorts.bot.utils import BRAND_COLOR, get_guild_university, clean_text

class ClubsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.club_service = ClubService()

    @nextcord.slash_command(name="clubs", description="List all university clubs in a paginated directory.")
    async def clubs(self, interaction: nextcord.Interaction):
        """Presents a paginated list of all clubs in the primary university."""
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

            # Fetch first page
            clubs, total_count = self.club_service.get_clubs_paginated(db, univ.id, page=1, per_page=3)
            
            if total_count == 0:
                await interaction.send("Sortling: 'Interesting... No clubs have been published yet.'", ephemeral=True)
                return

            view = ClubPagingView(univ.id, 1, 3, total_count, univ.primary_color)
            await interaction.send(embed=view.make_embed(clubs), view=view)

    @nextcord.slash_command(name="club", description="Search and view details of a specific university club.")
    async def club(
        self,
        interaction: nextcord.Interaction,
        name: str = nextcord.SlashOption(description="Name or partial keywords of the club to search for")
    ):
        """Displays full information card for a specific club matching search terms."""
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

            matches = self.club_service.search_clubs(db, univ.id, name)
            
            if not matches:
                await interaction.send(
                    f"Sortling: 'Hmm... I couldn't find any club matching \"{name}\". Try checking the directory using `/clubs`!'",
                    ephemeral=True
                )
                return

            if len(matches) > 1:
                names_list = ", ".join(f"**{c.name}**" for c in matches[:5])
                await interaction.send(
                    f"Sortling: 'I found multiple clubs matching \"{name}\": {names_list}. Could you try being a bit more specific?'",
                    ephemeral=True
                )
                return

            club = matches[0]
            color = BRAND_COLOR

            embed = nextcord.Embed(
                title=clean_text(club.name),
                description=clean_text(f"*{club.summary}*\n\n{club.description}"),
                color=color
            )
            if club.image:
                embed.set_thumbnail(url=club.image)

            # Details
            freq = club.meeting_frequency or "Not specified"
            commit = club.commitment or "Not specified"
            embed.add_field(name="📅 Sessions Frequency", value=clean_text(freq), inline=True)
            embed.add_field(name="⏳ Commitment Level", value=clean_text(commit), inline=True)

            # Traits list
            traits_list = []
            for ct in club.traits:
                traits_list.append(f"• **{ct.trait.name}**: {ct.weight * 100:.0f}% weight")
            
            if traits_list:
                embed.add_field(name="🏷️ Key Club Traits", value=clean_text("\n".join(traits_list)), inline=False)

            socials = []
            if club.website and club.website != "-":
                socials.append(f"[Website]({club.website})")
            if club.discord and club.discord != "-":
                socials.append(f"[Discord]({club.discord})")
            if club.instagram and club.instagram != "-":
                socials.append(f"[Instagram]({club.instagram})")
            if club.email and club.email != "-":
                socials.append(f"[Email](mailto:{club.email})")

            if socials:
                embed.add_field(name="🔗 Get in touch", value=" | ".join(socials), inline=False)

            embed.set_footer(text=f"sorts.me Campus Guide: University ID: {univ.id}")
            await interaction.send(embed=embed)

def setup(bot):
    bot.add_cog(ClubsCog(bot))

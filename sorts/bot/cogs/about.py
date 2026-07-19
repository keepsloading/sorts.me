import nextcord
from nextcord.ext import commands
from sorts.database.connection import get_db
from sorts.bot.utils import create_sortling_embed, BRAND_COLOR, get_guild_university, clean_text


class AboutCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="about", description="Learn about sorts.me and how it works.")
    async def about(self, interaction: nextcord.Interaction):
        """Displays the university profile and a short explanation of the sorts.me guide."""
        try:
            with get_db() as db:
                univ = get_guild_university(db, interaction.guild_id)

                if not univ:
                    embed, file = create_sortling_embed(
                        title="Not Configured",
                        description="This server hasn't been linked to a university yet. Ask an administrator to run `/setup`.",
                        is_error=True,
                    )
                    await interaction.send(embed=embed, file=file, ephemeral=True)
                    return

                embed, file = create_sortling_embed(
                    title=f"sorts.me  ·  {univ.name}",
                    description=clean_text(univ.description or "Your campus club guide."),
                    is_error=False,
                )

                if univ.logo:
                    embed.set_thumbnail(url=univ.logo)

                embed.add_field(
                    name="How it works",
                    value=(
                        "Answer a short set of adaptive questions and sorts.me will match you "
                        "with clubs that fit your interests, skills, and availability.\n\n"
                        "Type `/sort` to get started."
                    ),
                    inline=False,
                )

                if univ.website:
                    embed.add_field(
                        name="Website",
                        value=f"[{univ.name}]({univ.website})",
                        inline=True,
                    )

                embed.set_footer(text="sorts.me")

                if file:
                    await interaction.send(embed=embed, file=file)
                else:
                    await interaction.send(embed=embed)

        except Exception as e:
            embed, file = create_sortling_embed(
                title="Something went wrong",
                description="Could not load the about page. Please try again.",
                is_error=True,
            )
            await interaction.send(embed=embed, file=file, ephemeral=True)


def setup(bot):
    bot.add_cog(AboutCog(bot))

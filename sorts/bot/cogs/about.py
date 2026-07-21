import nextcord
from nextcord.ext import commands
from sorts.database.connection import get_db
from sorts.bot.utils import create_sortling_embed, BRAND_COLOR, get_guild_university, clean_text


class AboutCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="about", description="Learn about Sortling and how it works.")
    async def about(self, interaction: nextcord.Interaction):
        """Displays the university profile and a short explanation of Sortling."""
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

                desc_parts = [
                    "> **Your campus, sorted.**",
                    "",
                    "## About",
                    "Sortling is your intelligent campus discovery engine. Designed to connect students with official campus clubs, hackathons, and student opportunities, Sortling matches you with communities aligned with your skills, interests, and availability.",
                    "",
                    "━━━━━━━━━━━━━━━━━━━━━━━",
                    "",
                    "## How it Works",
                    "• **Interactive Matching**: Type `/sort` to answer quick adaptive questions and receive personalized club recommendations.",
                    "• **Campus Clubs Directory**: Type `/clubs` or `/club <name>` to explore verified student organizations.",
                    "• **Hackathons & Opportunities**: Type `/events` or `/event <name>` to discover upcoming competitions, prizes, and registration details.",
                    "",
                    "━━━━━━━━━━━━━━━━━━━━━━━",
                    "",
                    "## Legal & Privacy",
                    "[Terms of Service](https://sortling-bot.onrender.com/terms)  ·  [Privacy Policy](https://sortling-bot.onrender.com/privacy)"
                ]

                embed, file = create_sortling_embed(
                    title="Sortling",
                    description="\n".join(desc_parts),
                    is_error=False,
                )
                embed.set_footer(text="Sortling • Intelligent Campus Discovery Engine")

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

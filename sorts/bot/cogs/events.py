import nextcord
from nextcord.ext import commands
from sorts.database.connection import get_db
from sorts.database import models as db_models
from sorts.bot.utils import create_sortling_embed, BRAND_COLOR, get_guild_university, clean_text


class RegisterButtonView(nextcord.ui.View):
    """View containing a direct action button for event registration."""
    def __init__(self, registration_url: str):
        super().__init__(timeout=None)
        self.add_item(
            nextcord.ui.Button(
                label="Register Now 🚀",
                url=registration_url or "https://qrco.de/bgvXHe",
                style=nextcord.ButtonStyle.link,
            )
        )


class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ─── /events ──────────────────────────────────────────────────────────────

    @nextcord.slash_command(name="events", description="Browse upcoming campus hackathons, competitions, and opportunities.")
    async def events(
        self,
        interaction: nextcord.Interaction,
        category: str = nextcord.SlashOption(
            description="Filter by category",
            choices=["All", "Hackathon", "Workshop", "Opportunity"],
            required=False,
            default="All",
        ),
    ):
        """Displays a list of upcoming campus events and hackathons."""
        try:
            with get_db() as db:
                univ = get_guild_university(db, interaction.guild_id)
                if not univ:
                    embed, file = create_sortling_embed(
                        title="Not Configured",
                        description="This server has not been linked to a university yet. Ask an administrator to run `/setup`.",
                        is_error=True,
                    )
                    await interaction.send(embed=embed, file=file, ephemeral=True)
                    return

                query = db.query(db_models.Event).filter_by(university_id=univ.id)
                if category and category != "All":
                    query = query.filter(db_models.Event.category.ilike(f"%{category}%"))

                events_list = query.all()

                if not events_list:
                    embed, file = create_sortling_embed(
                        title="No Upcoming Events",
                        description=f"No active events found for **{univ.name}** under `{category}`.",
                        is_error=False,
                    )
                    await interaction.send(embed=embed, file=file)
                    return

                embed, file = create_sortling_embed(
                    title=f"Campus Events & Opportunities  ·  {univ.name}",
                    description=f"Showing **{len(events_list)}** upcoming hackathons & opportunities for **{univ.name}**.\nType `/event <name>` for full registration details.",
                    is_error=False,
                )

                for ev in events_list[:10]:
                    badge = "🚀" if ev.category == "Hackathon" else "💡"
                    req_text = "📧 *Student Email Required*" if ev.email_required else ""
                    val = (
                        f"{clean_text(ev.summary)}\n"
                        f"📅 **Deadline**: {ev.registration_deadline or 'TBA'}  |  🗓️ **Date**: {ev.event_date or 'TBA'}\n"
                        f"{req_text}"
                    )
                    embed.add_field(
                        name=f"{badge} {ev.name}",
                        value=val,
                        inline=False,
                    )

                embed.set_footer(text="Sortling • Campus Opportunity Engine")

                if file:
                    await interaction.send(embed=embed, file=file)
                else:
                    await interaction.send(embed=embed)

        except Exception as e:
            embed, file = create_sortling_embed(
                title="Something went wrong",
                description=f"Could not fetch campus events.\n`{e}`",
                is_error=True,
            )
            await interaction.send(embed=embed, file=file, ephemeral=True)

    # ─── /event ───────────────────────────────────────────────────────────────

    @nextcord.slash_command(name="event", description="View detailed information, prizes, and registration for a specific event.")
    async def event_detail(
        self,
        interaction: nextcord.Interaction,
        name: str = nextcord.SlashOption(description="Name or keyword of the hackathon or event"),
    ):
        """Displays full Sortling-Native details for a specific event."""
        try:
            with get_db() as db:
                univ = get_guild_university(db, interaction.guild_id)
                if not univ:
                    embed, file = create_sortling_embed(
                        title="Not Configured",
                        description="This server has not been linked to a university yet. Ask an administrator to run `/setup`.",
                        is_error=True,
                    )
                    await interaction.send(embed=embed, file=file, ephemeral=True)
                    return

                # Search by exact slug or substring match
                ev = (
                    db.query(db_models.Event)
                    .filter(
                        db_models.Event.university_id == univ.id,
                        (db_models.Event.slug == name.lower()) | (db_models.Event.name.ilike(f"%{name}%")),
                    )
                    .first()
                )

                if not ev:
                    # Fallback search across all events
                    all_evs = db.query(db_models.Event).filter_by(university_id=univ.id).all()
                    ev = next((e for e in all_evs if name.lower() in e.name.lower() or name.lower() in e.slug), None)

                if not ev:
                    embed, file = create_sortling_embed(
                        title="Event Not Found",
                        description=f"Could not find an event matching **'{name}'**. Type `/events` to see all upcoming events.",
                        is_error=True,
                    )
                    await interaction.send(embed=embed, file=file, ephemeral=True)
                    return

                # Build Sortling-Native detailed embed
                embed, file = create_sortling_embed(
                    title=f"🚀 {ev.name}",
                    description=clean_text(ev.description),
                    is_error=False,
                )

                embed.add_field(
                    name="🏛️ Organized By",
                    value=clean_text(ev.organizer),
                    inline=True,
                )

                embed.add_field(
                    name="🏷️ Category",
                    value=f"`{ev.category}`",
                    inline=True,
                )

                if ev.registration_deadline or ev.event_date:
                    dates_str = f"• **Registration Deadline**: {ev.registration_deadline or 'N/A'}\n• **Event Date**: {ev.event_date or 'N/A'}"
                    embed.add_field(
                        name="📅 Important Dates",
                        value=dates_str,
                        inline=False,
                    )

                if ev.prizes:
                    embed.add_field(
                        name="🏆 Cash Prizes & Rewards",
                        value=clean_text(ev.prizes),
                        inline=False,
                    )

                if ev.team_rules:
                    embed.add_field(
                        name="👥 Team Formation Rules",
                        value=clean_text(ev.team_rules),
                        inline=False,
                    )

                if ev.email_required:
                    embed.add_field(
                        name="📧 Registration Requirement",
                        value="⚠️ **Student Email (@mahindrauniversity.edu.in) is required for registration.**",
                        inline=False,
                    )

                embed.set_footer(text="Sortling • Official Campus Hackathon & Opportunity Guide")

                view = RegisterButtonView(ev.registration_link)

                if file:
                    await interaction.send(embed=embed, file=file, view=view)
                else:
                    await interaction.send(embed=embed, view=view)

        except Exception as e:
            embed, file = create_sortling_embed(
                title="Something went wrong",
                description=f"Could not load event details.\n`{e}`",
                is_error=True,
            )
            await interaction.send(embed=embed, file=file, ephemeral=True)


def setup(bot):
    bot.add_cog(EventsCog(bot))

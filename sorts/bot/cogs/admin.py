import nextcord
from nextcord.ext import commands
from sorts.database.connection import get_db
from sorts.database import models as db_models
from sorts.services.import_service import ImportService
from sorts.bot.views.admin_preview import AdminPreviewView
from sorts.bot.utils import BRAND_COLOR, create_sortling_embed, get_guild_university, clean_text


def _is_admin(interaction: nextcord.Interaction) -> bool:
    if not interaction.user:
        return False
    if interaction.guild and interaction.guild.owner_id == interaction.user.id:
        return True
    if hasattr(interaction.user, "guild_permissions"):
        perms = interaction.user.guild_permissions
        return bool(perms.administrator or perms.manage_guild)
    return False


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.import_service = ImportService()

    # ─── /setup ───────────────────────────────────────────────────────────────

    @nextcord.slash_command(name="setup", description="Link this server to a university profile.")
    async def setup_university(
        self,
        interaction: nextcord.Interaction,
        name: str = nextcord.SlashOption(description="Full name of the university"),
        website: str = nextcord.SlashOption(description="Official website URL"),
        logo_url: str = nextcord.SlashOption(description="URL to the university logo", required=False),
        description: str = nextcord.SlashOption(description="Short one-line description", required=False),
    ):
        """Registers or updates this server's university profile."""
        if not _is_admin(interaction):
            embed, file = create_sortling_embed(
                title="Access Denied",
                description="Only server administrators can run setup.",
                is_error=True,
            )
            await interaction.send(embed=embed, file=file, ephemeral=True)
            return

        guild_id = interaction.guild_id
        if not guild_id:
            embed, file = create_sortling_embed(
                title="Server Only",
                description="This command can only be used inside a Discord server.",
                is_error=True,
            )
            await interaction.send(embed=embed, file=file, ephemeral=True)
            return

        from sorts.config.settings import EXEMPTED_GUILDS
        if guild_id in EXEMPTED_GUILDS:
            embed, file = create_sortling_embed(
                title="Already Configured",
                description="This server is pre-configured and does not need setup.",
                is_error=False,
            )
            await interaction.send(embed=embed, file=file, ephemeral=True)
            return

        try:
            with get_db() as db:
                univ = db.query(db_models.University).filter_by(guild_id=str(guild_id)).first()
                slug = f"guild_{guild_id}"

                if not univ:
                    univ = db_models.University(
                        slug=slug,
                        name=name,
                        website=website,
                        logo=logo_url,
                        description=description or f"Campus guide for {name}.",
                        guild_id=str(guild_id),
                    )
                    db.add(univ)
                    db.commit()
                    db.refresh(univ)
                    import_src = db_models.ImportSource(
                        university_id=univ.id,
                        name="Default Source",
                        source_type="file",
                        url=f"sorts/assets/data/{slug}_clubs.html",
                    )
                    db.add(import_src)
                    db.commit()
                    msg = f"**{name}** is now registered on Sortling. Use `/admin sync` whenever you want to update the club directory."
                else:
                    univ.name = name
                    univ.website = website
                    if logo_url:
                        univ.logo = logo_url
                    if description:
                        univ.description = description
                    db.commit()
                    msg = f"Profile updated for **{name}**."

                embed, file = create_sortling_embed(title="Setup Complete", description=msg, is_error=False)
                await interaction.send(embed=embed, file=file)
        except Exception as e:
            embed, file = create_sortling_embed(
                title="Setup Failed",
                description=f"Something went wrong. Please try again or contact support.\n`{e}`",
                is_error=True,
            )
            await interaction.send(embed=embed, file=file, ephemeral=True)

    # ─── /admin ───────────────────────────────────────────────────────────────

    @nextcord.slash_command(name="admin", description="Manage the club directory for this server.")
    async def admin(self, interaction: nextcord.Interaction):
        pass

    # ─── /admin sync ──────────────────────────────────────────────────────────

    @admin.subcommand(name="sync", description="Fetch the latest club data from the university website.")
    async def sync(self, interaction: nextcord.Interaction):
        """Crawls the configured source and stages changes for review."""
        if not _is_admin(interaction):
            embed, file = create_sortling_embed(
                title="Access Denied",
                description="Only server administrators can sync the club directory.",
                is_error=True,
            )
            await interaction.send(embed=embed, file=file, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        try:
            with get_db() as db:
                univ = get_guild_university(db, interaction.guild_id)
                if not univ:
                    embed, file = create_sortling_embed(
                        title="Not Configured",
                        description="Run `/setup` first to link this server to a university.",
                        is_error=True,
                    )
                    await interaction.followup.send(embed=embed, file=file, ephemeral=True)
                    return

                sources = self.import_service.get_university_sources(db, univ.id)
                if not sources:
                    embed, file = create_sortling_embed(
                        title="No Source Configured",
                        description="No club data source has been set up for this university. Contact a Sortling administrator.",
                        is_error=True,
                    )
                    await interaction.followup.send(embed=embed, file=file, ephemeral=True)
                    return

                # Use the first active source
                source = sources[0]
                job_id = self.import_service.trigger_import(db, source.id)

                embed, file = create_sortling_embed(
                    title="Sync Complete",
                    description=(
                        f"Club data has been fetched and is ready for review.\n\n"
                        f"Run `/admin review` to see what changed before publishing."
                    ),
                    is_error=False,
                )
                await interaction.followup.send(embed=embed, file=file, ephemeral=True)
        except Exception as e:
            embed, file = create_sortling_embed(
                title="Sync Failed",
                description=f"The sync could not complete. Please try again.\n`{e}`",
                is_error=True,
            )
            await interaction.followup.send(embed=embed, file=file, ephemeral=True)

    # ─── /admin review ────────────────────────────────────────────────────────

    @admin.subcommand(name="review", description="Preview pending club changes before they go live.")
    async def review(self, interaction: nextcord.Interaction):
        """Shows staged changes from the latest sync and lets admins approve them."""
        if not _is_admin(interaction):
            embed, file = create_sortling_embed(
                title="Access Denied",
                description="Only server administrators can review pending changes.",
                is_error=True,
            )
            await interaction.send(embed=embed, file=file, ephemeral=True)
            return

        try:
            with get_db() as db:
                univ = get_guild_university(db, interaction.guild_id)
                if not univ:
                    embed, file = create_sortling_embed(
                        title="Not Configured",
                        description="Run `/setup` first to link this server to a university.",
                        is_error=True,
                    )
                    await interaction.send(embed=embed, file=file, ephemeral=True)
                    return

                job = self.import_service.get_latest_job(db, univ.id)
                if not job:
                    embed, file = create_sortling_embed(
                        title="Nothing to Review",
                        description="No sync has been run yet. Use `/admin sync` to fetch the latest club data.",
                        is_error=False,
                    )
                    await interaction.send(embed=embed, file=file, ephemeral=True)
                    return

                if job.status == "approved":
                    embed, file = create_sortling_embed(
                        title="Already Published",
                        description="The most recent sync has already been published. Run `/admin sync` to fetch fresh data.",
                        is_error=False,
                    )
                    await interaction.send(embed=embed, file=file, ephemeral=True)
                    return

                diff = self.import_service.get_draft_diff(db, job.id)
                new_names = [f"+ {dc.name}" for dc in diff["new"]]
                up_names  = [f"~ {dc.name}" for dc in diff["updated"]]
                rem_names = [f"- {dc.name}" for dc in diff["removed"]]

                embed = nextcord.Embed(
                    title="Pending Club Changes",
                    description="Review the changes below, then click **Publish** to make them live.",
                    color=BRAND_COLOR,
                )
                embed.add_field(
                    name=f"New  ({len(new_names)})",
                    value=clean_text("\n".join(new_names) or "None"),
                    inline=True,
                )
                embed.add_field(
                    name=f"Updated  ({len(up_names)})",
                    value=clean_text("\n".join(up_names) or "None"),
                    inline=True,
                )
                embed.add_field(
                    name=f"Removed  ({len(rem_names)})",
                    value=clean_text("\n".join(rem_names) or "None"),
                    inline=True,
                )
                embed.set_footer(text="Publishing will immediately update the club directory for all students.")

                view = AdminPreviewView(job.id)
                await interaction.send(embed=embed, view=view, ephemeral=True)
        except Exception as e:
            embed, file = create_sortling_embed(
                title="Review Failed",
                description=f"Could not load pending changes.\n`{e}`",
                is_error=True,
            )
            await interaction.send(embed=embed, file=file, ephemeral=True)

    # ─── /admin publish ───────────────────────────────────────────────────────

    @admin.subcommand(name="publish", description="Immediately publish the latest synced club data.")
    async def publish(self, interaction: nextcord.Interaction):
        """Skips review and publishes the most recent sync directly."""
        if not _is_admin(interaction):
            embed, file = create_sortling_embed(
                title="Access Denied",
                description="Only server administrators can publish changes.",
                is_error=True,
            )
            await interaction.send(embed=embed, file=file, ephemeral=True)
            return

        try:
            with get_db() as db:
                univ = get_guild_university(db, interaction.guild_id)
                if not univ:
                    embed, file = create_sortling_embed(
                        title="Not Configured",
                        description="Run `/setup` first to link this server to a university.",
                        is_error=True,
                    )
                    await interaction.send(embed=embed, file=file, ephemeral=True)
                    return

                job = self.import_service.get_latest_job(db, univ.id)
                if not job:
                    embed, file = create_sortling_embed(
                        title="Nothing to Publish",
                        description="Run `/admin sync` to fetch the latest club data first.",
                        is_error=False,
                    )
                    await interaction.send(embed=embed, file=file, ephemeral=True)
                    return

                if job.status == "approved":
                    embed, file = create_sortling_embed(
                        title="Already Published",
                        description="The latest sync is already live. Run `/admin sync` to check for new changes.",
                        is_error=False,
                    )
                    await interaction.send(embed=embed, file=file, ephemeral=True)
                    return

                self.import_service.publish_job(db, job.id)
                embed, file = create_sortling_embed(
                    title="Published",
                    description="The club directory has been updated. Students will see the latest data immediately.",
                    is_error=False,
                )
                await interaction.send(embed=embed, file=file, ephemeral=True)
        except Exception as e:
            embed, file = create_sortling_embed(
                title="Publish Failed",
                description=f"Could not publish changes.\n`{e}`",
                is_error=True,
            )
            await interaction.send(embed=embed, file=file, ephemeral=True)

    # ─── /admin add_club ──────────────────────────────────────────────────────

    @admin.subcommand(name="add_club", description="Manually add a new student club to this server's university directory.")
    async def add_club(
        self,
        interaction: nextcord.Interaction,
        name: str = nextcord.SlashOption(description="Full name of the club"),
        summary: str = nextcord.SlashOption(description="Short one-line summary of what the club does"),
        description: str = nextcord.SlashOption(description="Detailed description of activities and goals"),
        category: str = nextcord.SlashOption(description="Category (e.g. Technology, Cultural, Sports)", required=False),
        commitment: str = nextcord.SlashOption(description="Commitment level (e.g. Low, Medium, High)", required=False),
        meeting_frequency: str = nextcord.SlashOption(description="Meeting schedule (e.g. Weekly, Bi-weekly)", required=False),
        website: str = nextcord.SlashOption(description="Official website or linktree URL", required=False),
        instagram: str = nextcord.SlashOption(description="Instagram profile URL", required=False),
        discord: str = nextcord.SlashOption(description="Discord invite URL", required=False),
    ):
        """Allows server administrators to manually register a new club into the database."""
        if not _is_admin(interaction):
            embed, file = create_sortling_embed(
                title="Access Denied",
                description="Only server owners and administrators can add new clubs.",
                is_error=True,
            )
            await interaction.send(embed=embed, file=file, ephemeral=True)
            return

        try:
            with get_db() as db:
                univ = get_guild_university(db, interaction.guild_id)
                if not univ:
                    embed, file = create_sortling_embed(
                        title="Not Configured",
                        description="Run `/setup` first to link this server to a university.",
                        is_error=True,
                    )
                    await interaction.send(embed=embed, file=file, ephemeral=True)
                    return

                import re
                base_slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
                slug = base_slug
                counter = 1
                while db.query(db_models.Club).filter_by(university_id=univ.id, slug=slug).first():
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                club = db_models.Club(
                    university_id=univ.id,
                    name=name,
                    slug=slug,
                    summary=summary,
                    description=description,
                    category=category or "General",
                    commitment=commitment or "Medium commitment",
                    meeting_frequency=meeting_frequency or "Bi-weekly sessions",
                    website=website,
                    instagram=instagram,
                    discord=discord,
                    official=True
                )
                club.set_verification(confidence=100, verified=True, source=["Admin Added"], last_verified="2026-07-21")
                db.add(club)
                db.commit()
                db.refresh(club)

                from sorts.core.traits.rule_trait_inferencer import RuleTraitInferencer
                inferencer = RuleTraitInferencer()
                trait_weights = inferencer.infer_traits(name=name, summary=summary, description=description, category=category or "General")

                for trait_slug, weight in trait_weights.items():
                    t_obj = db.query(db_models.Trait).filter_by(slug=trait_slug).first()
                    if t_obj:
                        ct = db_models.ClubTrait(club_id=club.id, trait_id=t_obj.id, weight=weight)
                        db.add(ct)
                db.commit()

                desc_parts = [
                    f"> **{name} has been added to the {univ.name} club directory.**",
                    "",
                    "## Club Details",
                    f"• **Category**: {category or 'General'}",
                    f"• **Summary**: {summary}",
                    f"• **Status**: Verified & active for `/sort` recommendations.",
                ]

                embed, file = create_sortling_embed(
                    title="Club Added Successfully",
                    description="\n".join(desc_parts),
                    is_error=False,
                )
                await interaction.send(embed=embed, file=file)
        except Exception as e:
            embed, file = create_sortling_embed(
                title="Failed to Add Club",
                description=f"Could not save the club entry.\n`{e}`",
                is_error=True,
            )
            await interaction.send(embed=embed, file=file, ephemeral=True)


def setup(bot):
    bot.add_cog(AdminCog(bot))

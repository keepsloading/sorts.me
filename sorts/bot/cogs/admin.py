import nextcord
from nextcord.ext import commands
from sorts.database.connection import get_db
from sorts.database import models as db_models
from sorts.services.import_service import ImportService
from sorts.bot.views.admin_preview import AdminPreviewView
from sorts.bot.utils import BRAND_COLOR, create_sortling_embed, get_guild_university, clean_text

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.import_service = ImportService()

    @nextcord.slash_command(name="setup", description="Configure university profile details for this Discord server.")
    async def setup_university(
        self,
        interaction: nextcord.Interaction,
        name: str = nextcord.SlashOption(description="Full name of the university"),
        website: str = nextcord.SlashOption(description="Official website URL"),
        logo_url: str = nextcord.SlashOption(description="URL to the university's logo image", required=False),
        description: str = nextcord.SlashOption(description="Short description of the university", required=False)
    ):
        """Sets up a unique university profile for this Discord server."""
        if not interaction.user.guild_permissions.administrator:
            embed, file = create_sortling_embed(
                title="Access Denied",
                description="Sortling: 'Oops! Only server administrators can configure university setups.'",
                color=BRAND_COLOR,
                is_error=True
            )
            await interaction.send(embed=embed, file=file, ephemeral=True)
            return

        guild_id = interaction.guild_id
        if not guild_id:
            await interaction.send("Sortling: 'Setup commands can only be run inside a Discord server.'", ephemeral=True)
            return

        # Excepted servers cannot be overwritten
        if guild_id in {1475575129726517349, 1361752080297230376}:
            await interaction.send("Sortling: 'This server is hardcoded to Mahindra University. No setup is needed here!'", ephemeral=True)
            return

        with get_db() as db:
            # Check if this guild already has a university
            univ = db.query(db_models.University).filter_by(guild_id=str(guild_id)).first()
            
            slug = f"guild_{guild_id}"
            
            if not univ:
                # Create new university profile
                univ = db_models.University(
                    slug=slug,
                    name=name,
                    website=website,
                    logo=logo_url,
                    description=description or f"Welcome to the matching guide for {name}.",
                    guild_id=str(guild_id)
                )
                db.add(univ)
                db.commit()
                db.refresh(univ)
                
                # Automatically add a default import source for this university
                import_src = db_models.ImportSource(
                    university_id=univ.id,
                    name="Default Simulated File Source",
                    source_type="file",
                    url=f"sorts/assets/data/{slug}_clubs.html"
                )
                db.add(import_src)
                db.commit()
                
                msg = f"Setup complete! University **{name}** has been registered (sorts.me ID: **{univ.id}**). You can now import clubs using `/admin`!"
            else:
                # Update existing profile
                univ.name = name
                univ.website = website
                if logo_url:
                    univ.logo = logo_url
                if description:
                    univ.description = description
                db.commit()
                msg = f"University profile updated! University **{name}** is configured (sorts.me ID: **{univ.id}**)."

            embed, file = create_sortling_embed(
                title="University Configuration Success",
                description=msg,
                is_error=False
            )
            await interaction.send(embed=embed, file=file)

    @nextcord.slash_command(name="admin", description="Admin commands to manage university crawler data.")
    async def admin(self, interaction: nextcord.Interaction):
        pass

    @admin.subcommand(name="import", description="Trigger an import crawl on a specific ImportSource.")
    async def trigger_import(
        self,
        interaction: nextcord.Interaction,
        source_id: int = nextcord.SlashOption(description="The ID of the ImportSource to run.")
    ):
        """Triggers crawling and trait inference on an import source."""
        if not interaction.user.guild_permissions.administrator:
            embed, file = create_sortling_embed(
                title="Access Denied",
                description="Sortling: 'Oops! Only university admins can teach me about the campus.'",
                color=BRAND_COLOR,
                is_error=True
            )
            await interaction.send(embed=embed, file=file, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        with get_db() as db:
            # Multi-tenant safety: Check if source belongs to the guild's university
            univ = get_guild_university(db, interaction.guild_id)
            if not univ:
                embed, file = create_sortling_embed(
                    title="Setup Required",
                    description="Sortling: 'This server has not been configured yet. Run `/setup` first!'",
                    is_error=True
                )
                await interaction.followup.send(embed=embed, file=file, ephemeral=True)
                return

            source = db.query(db_models.ImportSource).filter_by(id=source_id, university_id=univ.id).first()
            if not source:
                embed, file = create_sortling_embed(
                    title="Source Not Found",
                    description=f"Sortling: 'Hmm... I couldn't find an import source with ID {source_id} for this university.'",
                    is_error=True
                )
                await interaction.followup.send(embed=embed, file=file, ephemeral=True)
                return

            try:
                job_id = self.import_service.trigger_import(db, source_id)
                embed, file = create_sortling_embed(
                    title="Crawl Started Successfully",
                    description=(
                        f"Sortling: 'Finished running crawler! Job ID is **{job_id}**. "
                        f"To preview changes, type `/admin preview job_id: {job_id}`.'"
                    ),
                    color=BRAND_COLOR,
                    is_error=False
                )
                await interaction.followup.send(embed=embed, file=file, ephemeral=True)
            except Exception as e:
                embed, file = create_sortling_embed(
                    title="Import Failed",
                    description=f"Sortling: 'Uh-oh, something failed during crawling: `{str(e)}`.'",
                    color=BRAND_COLOR,
                    is_error=True
                )
                await interaction.followup.send(embed=embed, file=file, ephemeral=True)

    @admin.subcommand(name="preview", description="Preview crawled draft differences and approve publishing.")
    async def preview_drafts(
        self,
        interaction: nextcord.Interaction,
        job_id: int = nextcord.SlashOption(description="The ID of the ImportJob to review.")
    ):
        """Displays categorized draft changes and provides an approve/publish view."""
        if not interaction.user.guild_permissions.administrator:
            embed, file = create_sortling_embed(
                title="Access Denied",
                description="Sortling: 'Oops! Only university admins can teach me about the campus.'",
                color=BRAND_COLOR,
                is_error=True
            )
            await interaction.send(embed=embed, file=file, ephemeral=True)
            return

        with get_db() as db:
            univ = get_guild_university(db, interaction.guild_id)
            if not univ:
                embed, file = create_sortling_embed(
                    title="Setup Required",
                    description="Sortling: 'This server has not been configured yet. Run `/setup` first!'",
                    is_error=True
                )
                await interaction.send(embed=embed, file=file, ephemeral=True)
                return

            job = db.query(db_models.ImportJob).filter_by(id=job_id, university_id=univ.id).first()
            if not job:
                embed, file = create_sortling_embed(
                    title="Job Not Found",
                    description=f"Sortling: 'Hmm... I couldn't find an import job with ID {job_id} for this university.'",
                    color=BRAND_COLOR,
                    is_error=True
                )
                await interaction.send(embed=embed, file=file, ephemeral=True)
                return

            if job.status not in ["completed", "approved"]:
                embed, file = create_sortling_embed(
                    title="Invalid Job Status",
                    description=f"Sortling: 'Hmm... This job is in status `{job.status}`. I can only preview finished jobs.'",
                    color=BRAND_COLOR,
                    is_error=True
                )
                await interaction.send(embed=embed, file=file, ephemeral=True)
                return

            diff = self.import_service.get_draft_diff(db, job_id)
            
            new_names = [f"• {dc.name}" for dc in diff["new"]]
            up_names = [f"• {dc.name}" for dc in diff["updated"]]
            rem_names = [f"• {dc.name}" for dc in diff["removed"]]

            embed = nextcord.Embed(
                title=f"Draft Review: Job ID {job_id}",
                description=f"Review changes for University ID: {job.university_id} (Status: **{job.status}**)",
                color=BRAND_COLOR
            )
            
            embed.add_field(
                name=f"🟢 New Clubs ({len(new_names)})",
                value=clean_text("\n".join(new_names) if new_names else "None"),
                inline=True
            )
            embed.add_field(
                name=f"🟡 Updated Clubs ({len(up_names)})",
                value=clean_text("\n".join(up_names) if up_names else "None"),
                inline=True
            )
            embed.add_field(
                name=f"🔴 Removed Clubs ({len(rem_names)})",
                value=clean_text("\n".join(rem_names) if rem_names else "None"),
                inline=True
            )

            # Check if Neutral Icon Mascot file exists and attach
            file = None
            import os
            mascot_path = os.path.join("Sortling Mascot", "Icon_Neutral.png")
            if os.path.exists(mascot_path):
                file = nextcord.File(mascot_path, filename="Icon_Neutral.png")
                embed.set_thumbnail(url="attachment://Icon_Neutral.png")

            if job.status == "approved":
                embed.set_footer(text="Changes for this job have already been published.")
                if file:
                    await interaction.send(embed=embed, file=file, ephemeral=True)
                else:
                    await interaction.send(embed=embed, ephemeral=True)
            else:
                view = AdminPreviewView(job_id)
                if file:
                    await interaction.send(embed=embed, view=view, file=file, ephemeral=True)
                else:
                    await interaction.send(embed=embed, view=view, ephemeral=True)

    @admin.subcommand(name="publish", description="Force publish and approve a completed ImportJob.")
    async def force_publish(
        self,
        interaction: nextcord.Interaction,
        job_id: int = nextcord.SlashOption(description="The ID of the ImportJob to publish.")
    ):
        """Directly publishes a completed job without interactive view."""
        if not interaction.user.guild_permissions.administrator:
            embed, file = create_sortling_embed(
                title="Access Denied",
                description="Sortling: 'Oops! Only university admins can teach me about the campus.'",
                color=BRAND_COLOR,
                is_error=True
            )
            await interaction.send(embed=embed, file=file, ephemeral=True)
            return

        with get_db() as db:
            univ = get_guild_university(db, interaction.guild_id)
            if not univ:
                embed, file = create_sortling_embed(
                    title="Setup Required",
                    description="Sortling: 'This server has not been configured yet. Run `/setup` first!'",
                    is_error=True
                )
                await interaction.send(embed=embed, file=file, ephemeral=True)
                return

            job = db.query(db_models.ImportJob).filter_by(id=job_id, university_id=univ.id).first()
            if not job:
                embed, file = create_sortling_embed(
                    title="Job Not Found",
                    description=f"Sortling: 'Hmm... I couldn't find an import job with ID {job_id} for this university.'",
                    color=BRAND_COLOR,
                    is_error=True
                )
                await interaction.send(embed=embed, file=file, ephemeral=True)
                return

            try:
                self.import_service.publish_job(db, job_id)
                embed, file = create_sortling_embed(
                    title="Publish Success",
                    description=f"Sortling: 'I've approved and published Job ID **{job_id}**. The club list is now live!'",
                    color=BRAND_COLOR,
                    is_error=False
                )
                await interaction.send(embed=embed, file=file, ephemeral=True)
            except Exception as e:
                embed, file = create_sortling_embed(
                    title="Publish Failed",
                    description=f"Sortling: 'Oops! Failed to publish: `{str(e)}`.'",
                    color=BRAND_COLOR,
                    is_error=True
                )
                await interaction.send(embed=embed, file=file, ephemeral=True)

def setup(bot):
    bot.add_cog(AdminCog(bot))

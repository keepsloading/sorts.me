import nextcord
from nextcord.ext import commands
from sorts.database.connection import get_db
from sorts.database import models as db_models
from datetime import datetime
from sorts.bot.utils import get_guild_university, create_sortling_embed, BRAND_COLOR


class FeedbackCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="feedback", description="Rate your club recommendations.")
    async def feedback(
        self,
        interaction: nextcord.Interaction,
        rating: int = nextcord.SlashOption(
            description="How well did the matches fit? (1 = poor, 5 = excellent)",
            choices=[1, 2, 3, 4, 5],
        ),
        comments: str = nextcord.SlashOption(
            description="Anything you'd like to share about your matches?",
            required=False,
        ),
    ):
        """Records feedback tied to the user's most recent completed session."""
        user_id = str(interaction.user.id)

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

                latest_session = (
                    db.query(db_models.RecommendationSession)
                    .filter_by(user_identifier=user_id, university_id=univ.id, status="completed")
                    .order_by(db_models.RecommendationSession.completed_at.desc())
                    .first()
                )

                if not latest_session:
                    embed, file = create_sortling_embed(
                        title="No Session Found",
                        description="You haven't completed a matching session yet. Run `/sort` first.",
                        is_error=True,
                    )
                    await interaction.send(embed=embed, file=file, ephemeral=True)
                    return

                top_rec = (
                    db.query(db_models.Recommendation)
                    .filter_by(session_id=latest_session.id, rank=1)
                    .first()
                )

                if not top_rec:
                    embed, file = create_sortling_embed(
                        title="No Match Found",
                        description="Your session completed but no matches were recorded. Try running `/sort` again.",
                        is_error=True,
                    )
                    await interaction.send(embed=embed, file=file, ephemeral=True)
                    return

                existing = db.query(db_models.Feedback).filter_by(recommendation_id=top_rec.id).first()

                if existing:
                    existing.rating = rating
                    existing.comments = comments or existing.comments
                    existing.created_at = datetime.utcnow()
                    db.commit()
                    msg = "Your feedback has been updated. Thank you."
                else:
                    db.add(db_models.Feedback(
                        recommendation_id=top_rec.id,
                        rating=rating,
                        comments=comments,
                        created_at=datetime.utcnow(),
                    ))
                    db.commit()
                    msg = "Feedback received. It helps improve future matches."

                embed, file = create_sortling_embed(title="Feedback Saved", description=msg, is_error=False)
                await interaction.send(embed=embed, file=file, ephemeral=True)

        except Exception as e:
            embed, file = create_sortling_embed(
                title="Something went wrong",
                description="Could not save feedback. Please try again.",
                is_error=True,
            )
            await interaction.send(embed=embed, file=file, ephemeral=True)


def setup(bot):
    bot.add_cog(FeedbackCog(bot))

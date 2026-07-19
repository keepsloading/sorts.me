import nextcord
from nextcord.ext import commands
from sorts.database.connection import get_db
from sorts.database import models as db_models
from datetime import datetime
from sorts.bot.utils import get_guild_university

class FeedbackCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="feedback", description="Leave feedback for your recommended club matches.")
    async def feedback(
        self,
        interaction: nextcord.Interaction,
        rating: int = nextcord.SlashOption(
            description="Rating from 1 (poor) to 5 (excellent)",
            choices=[1, 2, 3, 4, 5]
        ),
        comments: str = nextcord.SlashOption(
            description="Any additional comments or suggestions for Sortling?",
            required=False
        )
    ):
        """Saves recommendation feedback linked to the user's latest completed session on this server."""
        user_id = str(interaction.user.id)
        
        with get_db() as db:
            univ = get_guild_university(db, interaction.guild_id)
            if not univ:
                await interaction.send(
                    "Sortling: 'This server hasn't been set up yet. Ask an admin to run `/setup`!'",
                    ephemeral=True
                )
                return

            # Find the user's latest completed session for this university
            latest_session = db.query(db_models.RecommendationSession)\
                .filter_by(user_identifier=user_id, university_id=univ.id, status="completed")\
                .order_by(db_models.RecommendationSession.completed_at.desc())\
                .first()

            if not latest_session:
                await interaction.send(
                    "Sortling: 'Hmm... It looks like you haven't completed a sorting session on this server yet. Type `/sort` first!'",
                    ephemeral=True
                )
                return

            # Find the top recommendation for this session
            top_rec = db.query(db_models.Recommendation)\
                .filter_by(session_id=latest_session.id, rank=1)\
                .first()

            if not top_rec:
                await interaction.send(
                    "Sortling: 'Interesting... I found your session but couldn't locate your matches. Try running `/sort` again!'",
                    ephemeral=True
                )
                return

            # Check if feedback already exists for this recommendation to avoid duplicates
            existing_fb = db.query(db_models.Feedback).filter_by(recommendation_id=top_rec.id).first()
            if existing_fb:
                existing_fb.rating = rating
                existing_fb.comments = comments or existing_fb.comments
                existing_fb.created_at = datetime.utcnow()
                db.commit()
                await interaction.send("Sortling: 'Ah, I updated your previous feedback! Thanks again!'", ephemeral=True)
            else:
                new_fb = db_models.Feedback(
                    recommendation_id=top_rec.id,
                    rating=rating,
                    comments=comments,
                    created_at=datetime.utcnow()
                )
                db.add(new_fb)
                db.commit()
                await interaction.send("Sortling: 'Awesome! Your feedback is logged. It helps me improve matching on this campus!'", ephemeral=True)

def setup(bot):
    bot.add_cog(FeedbackCog(bot))

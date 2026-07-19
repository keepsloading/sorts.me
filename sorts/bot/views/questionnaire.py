import nextcord
import os
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from sorts.database.connection import get_db
from sorts.services.session_service import SessionService
from sorts.database import models as db_models
from sorts.bot.utils import BRAND_COLOR, clean_text

logger = logging.getLogger(__name__)

class OptionButton(nextcord.ui.Button):
    def __init__(self, option_id: int, question_id: int, label: str, style: nextcord.ButtonStyle):
        super().__init__(label=label, style=style)
        self.option_id = option_id
        self.question_id = question_id

    async def callback(self, interaction: nextcord.Interaction):
        view: 'QuestionnaireView' = self.view
        # Submit the user's choice
        with get_db() as db:
            view.session_service.submit_answer(db, view.session_id, self.question_id, self.option_id)
            
            # Fetch the next question
            next_q = view.session_service.get_next_question(db, view.session_id)
            
            if next_q:
                # Update the view with the next question's buttons
                view.update_question(next_q)
                
                # Build embed for next question. Reuses the original thinking.gif attachment
                embed = nextcord.Embed(
                    title=clean_text(f"sorts.me: Question {view.question_count}"),
                    description=f"### {clean_text(next_q.text)}",
                    color=BRAND_COLOR
                )
                embed.set_thumbnail(url="attachment://thinking.gif")
                embed.set_footer(text="Sortling: 'One more question...'")
                
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                # No more questions! Generate recommendations. Show the thinking GIF animation!
                calculating_embed = nextcord.Embed(
                    description="### Sortling: 'I have a theory. Let me calculate...'", 
                    color=BRAND_COLOR
                )
                calculating_embed.set_thumbnail(url="attachment://thinking.gif")
                
                await interaction.response.edit_message(
                    embed=calculating_embed,
                    view=None
                )
                
                # Calculate recommendation match details
                recs = view.session_service.generate_recommendations(db, view.session_id, limit=3)
                
                # Fetch university logo and colors
                univ = db.query(db_models.University).filter_by(id=recs[0].session.university_id).first() if recs else None
                
                embed = nextcord.Embed(
                    title=clean_text("Sortling's Guide: Match Results!"),
                    description=clean_text(f"Here are the top clubs matched for you at **{univ.name if univ else 'your campus'}**:"),
                    color=BRAND_COLOR
                )
                
                # Attach mascot neutral icon to new follow-up results card
                file = None
                mascot_path = os.path.join("Sortling Mascot", "Icon_Neutral.png")
                if os.path.exists(mascot_path):
                    file = nextcord.File(mascot_path, filename="Icon_Neutral.png")
                    embed.set_thumbnail(url="attachment://Icon_Neutral.png")
                
                for r in recs:
                    club = r.club
                    
                    # Social connect links are removed for match results to optimize cognitive load and UI spacing

                    embed.add_field(
                        name=f"🏆 Rank {r.rank}: {clean_text(club.name)}",
                        value=(
                            f"**Summary:** {clean_text(club.summary)}\n\n"
                            f"**Why you fit:** {clean_text(r.explanation)}"
                        ),
                        inline=False
                    )
                
                embed.set_footer(text="To leave feedback on these results, use /feedback [rating] [comments]")
                
                if file:
                    await interaction.followup.send(embed=embed, file=file)
                else:
                    await interaction.followup.send(embed=embed)


class QuestionnaireView(nextcord.ui.View):
    def __init__(self, session_id: str, initial_q: db_models.Question):
        super().__init__(timeout=180.0)
        self.session_id = session_id
        self.session_service = SessionService()
        self.question_count = 1
        self.update_question(initial_q)

    def update_question(self, question: db_models.Question):
        """Clears existing buttons and adds new ones for the current question options."""
        self.clear_items()
        styles = [
            nextcord.ButtonStyle.green,
            nextcord.ButtonStyle.secondary,
            nextcord.ButtonStyle.danger,
            nextcord.ButtonStyle.blurple
        ]
        
        for idx, opt in enumerate(question.options):
            style = styles[idx % len(styles)]
            btn = OptionButton(
                option_id=opt.id,
                question_id=question.id,
                label=opt.text,
                style=style
            )
            self.add_item(btn)
        
        self.question_count += 1

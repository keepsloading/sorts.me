import nextcord
import os
import logging

from sorts.database.connection import get_db
from sorts.services.session_service import SessionService
from sorts.database import models as db_models
from sorts.bot.utils import BRAND_COLOR, create_sortling_embed, clean_text

logger = logging.getLogger(__name__)

RANK_MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}


class OptionButton(nextcord.ui.Button):
    def __init__(self, option_id: int, question_id: int, label: str, style: nextcord.ButtonStyle):
        super().__init__(label=label, style=style)
        self.option_id = option_id
        self.question_id = question_id

    async def callback(self, interaction: nextcord.Interaction):
        view: "QuestionnaireView" = self.view

        try:
            with get_db() as db:
                view.session_service.submit_answer(db, view.session_id, self.question_id, self.option_id)
                next_q = view.session_service.get_next_question(db, view.session_id)

                if next_q:
                    view.advance(next_q)
                    embed = nextcord.Embed(
                        title=clean_text(next_q.text),
                        color=BRAND_COLOR,
                    )
                    embed.set_footer(
                        text=f"Question {view.question_number} of {view.total_questions}  ·  sorts.me"
                    )
                    embed.set_thumbnail(url="attachment://thinking.gif")
                    await interaction.response.edit_message(embed=embed, view=view)

                else:
                    # Show a brief loading state while computing
                    loading_embed = nextcord.Embed(
                        description="Finding your matches...",
                        color=BRAND_COLOR,
                    )
                    loading_embed.set_thumbnail(url="attachment://thinking.gif")
                    await interaction.response.edit_message(embed=loading_embed, view=None)

                    recs = view.session_service.generate_recommendations(db, view.session_id, limit=3)

                    if not recs:
                        embed, file = create_sortling_embed(
                            title="No Matches Found",
                            description="No clubs matched your profile. Try running `/sort` again with different answers.",
                            is_error=True,
                        )
                        if file:
                            await interaction.followup.send(embed=embed, file=file)
                        else:
                            await interaction.followup.send(embed=embed)
                        return

                    univ = db.query(db_models.University).filter_by(
                        id=recs[0].session.university_id
                    ).first()
                    univ_name = univ.name if univ else "your campus"

                    embed = nextcord.Embed(
                        title="Your Club Matches",
                        description=f"Based on your answers, here are the best-fit clubs at **{univ_name}**.",
                        color=BRAND_COLOR,
                    )

                    for r in recs:
                        club = r.club
                        medal = RANK_MEDALS.get(r.rank, f"#{r.rank}")
                        embed.add_field(
                            name=f"{medal}  {clean_text(club.name)}",
                            value=(
                                f"> {clean_text(club.summary)}\n\n"
                                f"**Why you fit** — {clean_text(r.explanation)}"
                            ),
                            inline=False,
                        )

                    embed.set_footer(text="Rate your matches with /feedback  ·  sorts.me")

                    icon_path = os.path.join("Sortling Mascot", "Icon_Neutral.png")
                    file = None
                    if os.path.exists(icon_path):
                        file = nextcord.File(icon_path, filename="Icon_Neutral.png")
                        embed.set_thumbnail(url="attachment://Icon_Neutral.png")

                    if file:
                        await interaction.followup.send(embed=embed, file=file)
                    else:
                        await interaction.followup.send(embed=embed)

        except Exception as e:
            logger.error(f"Questionnaire error: {e}", exc_info=True)
            embed, file = create_sortling_embed(
                title="Something went wrong",
                description="An error occurred. Please try running `/sort` again.",
                is_error=True,
            )
            try:
                if file:
                    await interaction.followup.send(embed=embed, file=file, ephemeral=True)
                else:
                    await interaction.followup.send(embed=embed, ephemeral=True)
            except Exception:
                pass


class QuestionnaireView(nextcord.ui.View):
    def __init__(self, session_id: str, initial_q: db_models.Question, total_questions: int):
        super().__init__(timeout=300.0)
        self.session_id = session_id
        self.session_service = SessionService()
        self.total_questions = total_questions
        self.question_number = 1
        self._populate_buttons(initial_q)

    def advance(self, question: db_models.Question):
        """Move to the next question, updating buttons and counter."""
        self.question_number += 1
        self._populate_buttons(question)

    def _populate_buttons(self, question: db_models.Question):
        """Rebuild buttons for the current question."""
        self.clear_items()
        styles = [
            nextcord.ButtonStyle.green,
            nextcord.ButtonStyle.secondary,
            nextcord.ButtonStyle.danger,
            nextcord.ButtonStyle.blurple,
        ]
        for idx, opt in enumerate(question.options):
            btn = OptionButton(
                option_id=opt.id,
                question_id=question.id,
                label=opt.text,
                style=styles[idx % len(styles)],
            )
            self.add_item(btn)

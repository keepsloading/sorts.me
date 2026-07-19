import uuid
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
import logging

from sorts.core.domain.exceptions import SessionNotFoundException, QuestionNotFoundException
from sorts.core.domain import entities as domain_ent
from sorts.core.recommendation.deterministic_engine import DeterministicRecommendationEngine
from sorts.core.recommendation.explanation_generator import ExplanationGenerator
from sorts.core.questions.variance_selector import VarianceQuestionSelector
from sorts.database import models as db_models

logger = logging.getLogger(__name__)

class SessionService:
    def __init__(self):
        self.question_selector = VarianceQuestionSelector()
        self.explanation_generator = ExplanationGenerator()

    def create_session(self, db: Session, university_id: int, user_identifier: Optional[str] = None) -> db_models.RecommendationSession:
        """Creates a new recommendation session for a student."""
        session_id = str(uuid.uuid4())
        session = db_models.RecommendationSession(
            id=session_id,
            university_id=university_id,
            user_identifier=user_identifier,
            status="active",
            created_at=datetime.utcnow()
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        logger.info(f"Created session {session_id} for university {university_id}")
        return session

    def get_session(self, db: Session, session_id: str) -> Optional[db_models.RecommendationSession]:
        return db.query(db_models.RecommendationSession).filter_by(id=session_id).first()

    def get_next_question(self, db: Session, session_id: str) -> Optional[db_models.Question]:
        """Returns the next question to ask using the VarianceQuestionSelector."""
        session = self.get_session(db, session_id)
        if not session:
            raise SessionNotFoundException(session_id)

        # 1. Fetch answered question IDs
        answered_q_ids = [ans.question_id for ans in session.answers]

        # 2. Get unasked questions
        unasked_db_questions = db.query(db_models.Question)\
            .filter(db_models.Question.university_id == session.university_id)\
            .filter(~db_models.Question.id.in_(answered_q_ids) if answered_q_ids else True)\
            .all()

        if not unasked_db_questions:
            return None

        # 3. Get all clubs for candidate comparison
        db_clubs = db.query(db_models.Club).filter_by(university_id=session.university_id).all()
        if not db_clubs:
            return unasked_db_questions[0]

        # 4. Map DB models to Domain models
        domain_questions = [self._map_question(q) for q in unasked_db_questions]
        domain_clubs = [self._map_club(c) for c in db_clubs]
        
        session_traits = {st.trait.slug: st.value for st in session.traits}

        # 5. Run question selector
        selected_domain_q = self.question_selector.select_next_question(
            domain_questions, session_traits, domain_clubs
        )

        if not selected_domain_q:
            return None

        # Return the original DB question model
        return db.query(db_models.Question).filter_by(id=selected_domain_q.id).first()

    def submit_answer(self, db: Session, session_id: str, question_id: int, option_id: int) -> None:
        """Saves a student's answer and adjusts session traits based on option modifiers."""
        session = self.get_session(db, session_id)
        if not session:
            raise SessionNotFoundException(session_id)

        db_option = db.query(db_models.QuestionOption).filter_by(id=option_id, question_id=question_id).first()
        if not db_option:
            raise ValueError(f"Option {option_id} does not belong to question {question_id}.")

        # Log answer
        ans = db_models.SessionAnswer(
            session_id=session_id,
            question_id=question_id,
            option_id=option_id,
            answered_at=datetime.utcnow()
        )
        db.add(ans)

        # Apply trait modifiers
        for mod in db_option.trait_modifiers:
            st = db.query(db_models.SessionTrait).filter_by(session_id=session_id, trait_id=mod.trait_id).first()
            if not st:
                st = db_models.SessionTrait(
                    session_id=session_id,
                    trait_id=mod.trait_id,
                    value=0.0
                )
                db.add(st)
            # Add modifier weight to session trait value, clamped to [-1.0, 1.0]
            st.value = max(-1.0, min(1.0, st.value + mod.weight))
        
        db.commit()
        logger.debug(f"Submitted answer for session {session_id}, question {question_id}, option {option_id}")

    def generate_recommendations(self, db: Session, session_id: str, limit: int = 3) -> List[db_models.Recommendation]:
        """Calculates final recommendations, generates explanations, saves them, and closes the session."""
        session = self.get_session(db, session_id)
        if not session:
            raise SessionNotFoundException(session_id)

        # Fetch traits and clubs
        db_clubs = db.query(db_models.Club).filter_by(university_id=session.university_id).all()
        db_traits = db.query(db_models.Trait).all()
        
        trait_names = {t.slug: t.name for t in db_traits}
        recommender = DeterministicRecommendationEngine(trait_names=trait_names)

        # Map to domain
        session_traits = {st.trait.slug: st.value for st in session.traits}
        domain_clubs = [self._map_club(c) for c in db_clubs]

        # Calculate recommendations
        evidence_list = recommender.calculate_recommendations(session_traits, domain_clubs)

        # Exclude existing recommendations for this session (clear previous runs)
        db.query(db_models.Recommendation).filter_by(session_id=session_id).delete()

        # Create final recommendations
        db_recs = []
        for index, ev in enumerate(evidence_list[:limit]):
            explanation = self.explanation_generator.generate_explanation(ev)
            
            rec = db_models.Recommendation(
                session_id=session_id,
                club_id=ev.club_id,
                score=ev.overall_score,
                rank=index + 1,
                explanation=explanation,
                created_at=datetime.utcnow()
            )
            db.add(rec)
            db_recs.append(rec)

        # Complete the session
        session.status = "completed"
        session.completed_at = datetime.utcnow()
        db.commit()
        
        # Refresh models to bind them to the session
        for r in db_recs:
            db.refresh(r)

        # Collect and log all user responses, final traits, and matches for analytics/improvement
        logger.info("=== sorts.me: Session matching analytics ===")
        logger.info(f"Session ID: {session_id} | University ID: {session.university_id} | User: {session.user_identifier or 'Guest'}")
        logger.info("User Answers:")
        for idx, ans in enumerate(session.answers):
            logger.info(f"  Question {idx+1} ({ans.question.code}): {ans.option.text}")
        logger.info("Session Trait Vector:")
        for t_slug, val in session_traits.items():
            logger.info(f"  {t_slug}: {val:.2f}")
        logger.info("Matched Clubs:")
        for r in db_recs:
            logger.info(f"  Rank {r.rank}: {r.club.name} (Score: {r.score:.3f})")
        logger.info("============================================")

        logger.info(f"Generated {len(db_recs)} recommendations for session {session_id}")
        return db_recs

    # MAPPING HELPERS
    def _map_club(self, db_club: db_models.Club) -> domain_ent.Club:
        return domain_ent.Club(
            id=db_club.id,
            university_id=db_club.university_id,
            name=db_club.name,
            slug=db_club.slug,
            summary=db_club.summary,
            description=db_club.description,
            website=db_club.website,
            discord=db_club.discord,
            instagram=db_club.instagram,
            email=db_club.email,
            image=db_club.image,
            meeting_frequency=db_club.meeting_frequency,
            commitment=db_club.commitment,
            traits=[domain_ent.ClubTraitValue(trait_slug=ct.trait.slug, weight=ct.weight) for ct in db_club.traits]
        )

    def _map_question(self, db_q: db_models.Question) -> domain_ent.Question:
        options = []
        for opt in db_q.options:
            modifiers = [
                domain_ent.OptionTraitModifier(trait_slug=mod.trait.slug, weight=mod.weight)
                for mod in opt.trait_modifiers
            ]
            options.append(domain_ent.QuestionOption(
                id=opt.id,
                question_id=opt.question_id,
                text=opt.text,
                trait_modifiers=modifiers
            ))
        return domain_ent.Question(
            id=db_q.id,
            university_id=db_q.university_id,
            text=db_q.text,
            code=db_q.code,
            options=options
        )

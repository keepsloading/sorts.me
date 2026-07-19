import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sorts.database.connection import Base

class University(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    website = Column(String(255), nullable=False)
    logo = Column(String(255), nullable=True)
    primary_color = Column(String(7), nullable=True)  # Hex code
    secondary_color = Column(String(7), nullable=True)  # Hex code
    description = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True, default="{}")
    guild_id = Column(String(50), nullable=True, unique=True, index=True)

    # Relationships
    sources = relationship("ImportSource", back_populates="university", cascade="all, delete-orphan")
    clubs = relationship("Club", back_populates="university", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="university", cascade="all, delete-orphan")
    sessions = relationship("RecommendationSession", back_populates="university", cascade="all, delete-orphan")

    def get_metadata(self):
        try:
            return json.loads(self.metadata_json or "{}")
        except Exception:
            return {}

    def set_metadata(self, val):
        self.metadata_json = json.dumps(val or {})


class ImportSource(Base):
    __tablename__ = "import_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    source_type = Column(String(50), nullable=False)  # "website", "file"
    url = Column(String(255), nullable=False)
    parser_config_json = Column(Text, nullable=True, default="{}")
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    university = relationship("University", back_populates="sources")
    jobs = relationship("ImportJob", back_populates="source", cascade="all, delete-orphan")

    def get_parser_config(self):
        try:
            return json.loads(self.parser_config_json or "{}")
        except Exception:
            return {}

    def set_parser_config(self, val):
        self.parser_config_json = json.dumps(val or {})


class ImportJob(Base):
    __tablename__ = "import_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(Integer, ForeignKey("import_sources.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False, default="pending")  # "pending", "running", "completed", "failed", "approved"
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    source = relationship("ImportSource", back_populates="jobs")
    draft_clubs = relationship("DraftClub", back_populates="job", cascade="all, delete-orphan")


class Trait(Base):
    __tablename__ = "traits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)


class Club(Base):
    __tablename__ = "clubs"
    __table_args__ = (UniqueConstraint("university_id", "slug", name="uq_club_university_slug"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), nullable=False, index=True)
    summary = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    website = Column(String(255), nullable=True)
    discord = Column(String(255), nullable=True)
    instagram = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    image = Column(String(255), nullable=True)
    meeting_frequency = Column(String(100), nullable=True)
    commitment = Column(String(100), nullable=True)
    metadata_json = Column(Text, nullable=True, default="{}")

    # Relationships
    university = relationship("University", back_populates="clubs")
    traits = relationship("ClubTrait", back_populates="club", cascade="all, delete-orphan")

    def get_metadata(self):
        try:
            return json.loads(self.metadata_json or "{}")
        except Exception:
            return {}

    def set_metadata(self, val):
        self.metadata_json = json.dumps(val or {})


class ClubTrait(Base):
    __tablename__ = "club_traits"

    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="CASCADE"), primary_key=True)
    trait_id = Column(Integer, ForeignKey("traits.id", ondelete="CASCADE"), primary_key=True)
    weight = Column(Float, nullable=False)  # 0.0 to 1.0

    # Relationships
    club = relationship("Club", back_populates="traits")
    trait = relationship("Trait")


class DraftClub(Base):
    __tablename__ = "draft_clubs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    import_job_id = Column(Integer, ForeignKey("import_jobs.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    summary = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    website = Column(String(255), nullable=True)
    discord = Column(String(255), nullable=True)
    instagram = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    image = Column(String(255), nullable=True)
    meeting_frequency = Column(String(100), nullable=True)
    commitment = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False, default="new")  # "new", "updated", "removed", "unchanged"

    # Relationships
    job = relationship("ImportJob", back_populates="draft_clubs")
    traits = relationship("DraftClubTrait", back_populates="draft_club", cascade="all, delete-orphan")


class DraftClubTrait(Base):
    __tablename__ = "draft_club_traits"

    draft_club_id = Column(Integer, ForeignKey("draft_clubs.id", ondelete="CASCADE"), primary_key=True)
    trait_id = Column(Integer, ForeignKey("traits.id", ondelete="CASCADE"), primary_key=True)
    weight = Column(Float, nullable=False)

    # Relationships
    draft_club = relationship("DraftClub", back_populates="traits")
    trait = relationship("Trait")


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (UniqueConstraint("university_id", "code", name="uq_question_university_code"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    code = Column(String(50), nullable=False, index=True)

    # Relationships
    university = relationship("University", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")


class QuestionOption(Base):
    __tablename__ = "question_options"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    text = Column(String(255), nullable=False)

    # Relationships
    question = relationship("Question", back_populates="options")
    trait_modifiers = relationship("OptionTraitModifier", back_populates="option", cascade="all, delete-orphan")


class OptionTraitModifier(Base):
    __tablename__ = "option_trait_modifiers"

    option_id = Column(Integer, ForeignKey("question_options.id", ondelete="CASCADE"), primary_key=True)
    trait_id = Column(Integer, ForeignKey("traits.id", ondelete="CASCADE"), primary_key=True)
    weight = Column(Float, nullable=False)  # negative or positive change

    # Relationships
    option = relationship("QuestionOption", back_populates="trait_modifiers")
    trait = relationship("Trait")


class RecommendationSession(Base):
    __tablename__ = "recommendation_sessions"

    id = Column(String(36), primary_key=True)  # UUID stored as string
    university_id = Column(Integer, ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    user_identifier = Column(String(100), nullable=True)  # Discord User ID or other ID
    status = Column(String(50), nullable=False, default="active")  # "active", "completed"
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    university = relationship("University", back_populates="sessions")
    traits = relationship("SessionTrait", back_populates="session", cascade="all, delete-orphan")
    answers = relationship("SessionAnswer", back_populates="session", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="session", cascade="all, delete-orphan")


class SessionTrait(Base):
    __tablename__ = "session_traits"

    session_id = Column(String(36), ForeignKey("recommendation_sessions.id", ondelete="CASCADE"), primary_key=True)
    trait_id = Column(Integer, ForeignKey("traits.id", ondelete="CASCADE"), primary_key=True)
    value = Column(Float, nullable=False)

    # Relationships
    session = relationship("RecommendationSession", back_populates="traits")
    trait = relationship("Trait")


class SessionAnswer(Base):
    __tablename__ = "session_answers"

    session_id = Column(String(36), ForeignKey("recommendation_sessions.id", ondelete="CASCADE"), primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True)
    option_id = Column(Integer, ForeignKey("question_options.id", ondelete="CASCADE"), nullable=False)
    answered_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    session = relationship("RecommendationSession", back_populates="answers")
    question = relationship("Question")
    option = relationship("QuestionOption")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("recommendation_sessions.id", ondelete="CASCADE"), nullable=False)
    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    session = relationship("RecommendationSession", back_populates="recommendations")
    club = relationship("Club")
    feedbacks = relationship("Feedback", back_populates="recommendation", cascade="all, delete-orphan")


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    recommendation = relationship("Recommendation", back_populates="feedbacks")

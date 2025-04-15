from datetime import datetime
from sqlalchemy import NullPool, create_engine, Column, Integer, String, ForeignKey, Enum, Date
from sqlalchemy.orm import sessionmaker, relationship
from database.db_models_general import Base
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
# Set echo=False to silence logs, NullPool to ensure connections are not kept open too long
engine = create_engine(DATABASE_URL, echo=False, poolclass=NullPool)

# Verb Table (For Tracking Irregular Verbs)


class Verb(Base):
    __tablename__ = "verbs"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    infinitive = Column(String, unique=True, nullable=False)  # e.g., "sehen"
    past_simple = Column(String, nullable=False)  # e.g., "sah"
    past_participle = Column(String, nullable=False)  # e.g., "gesehen"

    exercises = relationship("VerbExercise", back_populates="verb")

# Noun Table (For Tracking Articles)


class NounArticlesRegular(Base):
    __tablename__ = "noun_articles_regular"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    word = Column(String, unique=True, nullable=False)  # e.g., "Tisch"
    article = Column(
        Enum("der", "die", "das", name="article_enum"), nullable=False)
    exercises = relationship("NounArticleRegularExercise", back_populates="noun")
    
class NounArticlesIrregular(Base):
    __tablename__ = "noun_articles_irregular"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    word = Column(String, unique=True, nullable=False)  # e.g., "Tisch"
    article = Column(
        Enum("der", "die", "das", name="article_enum"), nullable=False)
    exercises = relationship("NounArticleIrregularExercise", back_populates="noun")

# Verb Exercise Table


class VerbExercise(Base):
    __tablename__ = "verb_exercises"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    verb_id = Column(Integer, ForeignKey("verbs.id"))
    difficulty = Column(Integer)

    user = relationship("User")
    verb = relationship("Verb", back_populates="exercises")

# Noun Article Exercise Table


class NounArticleRegularExercise(Base):
    __tablename__ = "noun_articles_regular_exercises"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    noun_id = Column(Integer, ForeignKey("noun_articles_regular.id"))
    difficulty = Column(Integer)

    user = relationship("User")
    noun = relationship("NounArticlesRegular", back_populates="exercises")
    
class NounArticleIrregularExercise(Base):
    __tablename__ = "noun_articles_irregular_exercises"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    noun_id = Column(Integer, ForeignKey("noun_articles_irregular.id"))
    difficulty = Column(Integer)

    user = relationship("User")
    noun = relationship("NounArticlesIrregular", back_populates="exercises")

class DateEntry(Base):
    __tablename__ = "practice_times"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    practice_count = Column(Integer)
    date = Column(Date, default=lambda: datetime.date.today(), unique=True)
    
class WritingExercise(Base):
    __tablename__ = "writing_exercises"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    prompt = Column(String)
    level = Column(String)
    answer = Column(String)
    correction = Column(String)

class WritingTopic(Base):
    __tablename__ = "writing_topics"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    prompt = Column(String)
    level = Column(String)

class ReadingExercise(Base):
    __tablename__ = "reading_exercises"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    text = Column(String)
    level = Column(String)
    score = Column(Integer)
    total_questions = Column(Integer)

# Apply the changes
Base.metadata.create_all(engine)

# Create a session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

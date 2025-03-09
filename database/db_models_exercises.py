from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import sessionmaker, relationship
from db_models_general import Base

# Define the SQLite database
DATABASE_URL = "sqlite:///language_trainer.db"
# Set echo=False to silence logs
engine = create_engine(DATABASE_URL, echo=True)

# Verb Table (For Tracking Irregular Verbs)


class Verb(Base):
    __tablename__ = "verbs"

    id = Column(Integer, primary_key=True)
    infinitive = Column(String, unique=True, nullable=False)  # e.g., "sehen"
    past_simple = Column(String, nullable=False)  # e.g., "sah"
    past_participle = Column(String, nullable=False)  # e.g., "gesehen"

    exercises = relationship("VerbExercise", back_populates="verb")

# Noun Table (For Tracking Articles)


class Noun(Base):
    __tablename__ = "nouns"

    id = Column(Integer, primary_key=True)
    word = Column(String, unique=True, nullable=False)  # e.g., "Tisch"
    article = Column(
        Enum("der", "die", "das", name="article_enum"), nullable=False)
    exercises = relationship("NounExercise", back_populates="noun")

# Verb Exercise Table


class VerbExercise(Base):
    __tablename__ = "verb_exercises"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    verb_id = Column(Integer, ForeignKey("verbs.id"))
    correct = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    verb = relationship("Verb", back_populates="exercises")

# Noun Article Exercise Table


class NounExercise(Base):
    __tablename__ = "noun_exercises"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    noun_id = Column(Integer, ForeignKey("nouns.id"))
    correct = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    noun = relationship("Noun", back_populates="exercises")


# Apply the changes
Base.metadata.create_all(engine)

# Create a session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

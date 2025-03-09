from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

# Define the SQLite database
DATABASE_URL = "sqlite:///database/language_trainer.db"
# Set echo=False to silence logs
engine = create_engine(DATABASE_URL, echo=True)

# Base class for our ORM models
Base = declarative_base()

# User Model


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    # Relationship with exercises
    exercises = relationship("Exercise", back_populates="user")

# Vocabulary Model


class Vocabulary(Base):
    __tablename__ = "vocabulary"

    id = Column(Integer, primary_key=True)
    word = Column(String, unique=True, nullable=False)
    translation = Column(String)
    # Higher difficulty = more mistakes
    difficulty = Column(Integer, default=0)

    # Relationship with exercises
    exercises = relationship("Exercise", back_populates="word")

# Exercise Model (Tracks User Performance)


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    word_id = Column(Integer, ForeignKey("vocabulary.id"))
    correct = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="exercises")
    word = relationship("Vocabulary", back_populates="exercises")


# Create all tables
Base.metadata.create_all(engine)

# Create a session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

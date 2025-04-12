from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_DICT_URL")

# DATABASE_URL = "sqlite:///dict_database.db"

engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()


class DictionaryEntry(Base):
    __tablename__ = "dictionary_info"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    word = Column(String)
    forms = Column(String)
    derived = Column(String)
    related = Column(String)
    synonyms = Column(String)
    antonyms = Column(String)
    senses = Column(String)
    glosses = Column(String)
    examples = Column(String)
    
class CategoryEntry(Base):
    __tablename__ = "category_info"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    word = Column(String)
    forms = Column(String)
    senses = Column(String)
    glosses = Column(String)
    examples = Column(String)
    category = Column(String)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

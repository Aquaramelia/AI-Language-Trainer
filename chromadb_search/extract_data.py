from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.db_models_general import Vocabulary  
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def fetch_vocab():
    return session.query(Vocabulary).all()
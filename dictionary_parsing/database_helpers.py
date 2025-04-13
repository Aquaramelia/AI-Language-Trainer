from database_models import DictionaryEntry, SessionLocal, CategoryEntry

import sys
import os
# Get absolute path to the 'database' folder
database_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database'))

# Append to system path
if database_path not in sys.path:
    sys.path.append(database_path)
from db_models_general import Vocabulary
from db_models_general import SessionLocal as SessionLocal_maindb

def check_existing_vocabulary(word):
    session = SessionLocal_maindb()
    existing_word = session.query(Vocabulary).filter(Vocabulary.word.ilike(f"%{word}%")).first()
    session.close()
    if existing_word:
        print("Word found: ", word)
        return True
    else:
        return False
    

def add_dict_entry(
    word,
    forms,
    derived,
    related,
    synonyms,
    antonyms,
    senses,
    glosses,
    examples
):
    if not check_existing_vocabulary(word=word):
        print("Was not added to dictionary: ", word)
    else:
        session = SessionLocal()
        existing_entry = session.query(DictionaryEntry).filter_by(word=word).first()
        if existing_entry: 
            print("Existing in dictionary: ", word)
        else:
            entry = DictionaryEntry(
                word=word,
                forms=forms,
                derived=derived,
                related=related,
                synonyms=synonyms,
                antonyms=antonyms,
                senses=senses,
                glosses=glosses,
                examples=examples
            )
            session.add(entry)
            session.commit()
            print("Added to dictionary: ", word)
        session.close()
    
    
def add_cat_entry(
    word,
    forms,
    senses,
    glosses,
    examples,
    hyponyms,
    synonyms,
    antonyms,
    derived,
    related,
    category,
    index
):
    session = SessionLocal()
    existing_entry = session.query(CategoryEntry).filter_by(word=word).first()
    if existing_entry:
        print("Updating existing entry:", word)
        existing_entry.forms = forms
        existing_entry.senses = senses
        existing_entry.glosses = glosses
        existing_entry.examples = examples
        existing_entry.hyponyms = hyponyms
        existing_entry.antonyms = antonyms
        existing_entry.synonyms = synonyms
        existing_entry.related = related
        existing_entry.derived = derived
        existing_entry.category = category
    else:
        entry = CategoryEntry(
            word=word,
            forms=forms,
            senses=senses,
            glosses=glosses,
            examples=examples,
            hyponyms=hyponyms,
            antonyms=antonyms,
            synonyms=synonyms,
            related=related,
            derived=derived,
            category=category
        )
        session.add(entry)
        print("Added to dictionary: ", word, f"[{index} words remaining]")
    session.commit()  
    session.close()
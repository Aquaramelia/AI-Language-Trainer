from sqlalchemy import func
from database.db_models_exercises import NounArticlesRegular, Verb
from database.db_models_general import SessionLocal, Vocabulary, User


def add_user(username, password):
    try:
        """Adds a new user to the database."""
        session = SessionLocal()
        user = User(username=username, password=password)
        session.add(user)
        session.commit()
        session.close()
    except Exception as e:
        print(f"User addition failed: {e}")


def add_word(word, translation):
    """Adds a new word to the vocabulary table."""
    try:
        session = SessionLocal()
        new_word = Vocabulary(word=word, translation=translation)
        session.add(new_word)
        session.commit()
        session.close()
    except Exception as e:
        print(f"Vocabulary word addition failed: {e}")

def add_verb(infinitive, past_simple, past_participle):
    try:
        """Adds a new verb to the database."""
        session = SessionLocal()
        verb = Verb(infinitive=infinitive, past_simple=past_simple,
                    past_participle=past_participle)
        session.add(verb)
        session.commit()
        session.close()
    except Exception as e:
        print(f"Verb addition failed: {e}")


def add_noun(word, article):
    try:
        """Adds a noun with its correct article."""
        session = SessionLocal()
        noun = NounArticlesRegular(word=word, article=article)
        session.add(noun)
        session.commit()
        session.close()
    except Exception as e:
        print(f"Noun addition failed: {e}")


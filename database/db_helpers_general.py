from sqlalchemy import func
from database.db_models_exercises import Noun, Verb
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
        noun = Noun(word=word, article=article)
        session.add(noun)
        session.commit()
        session.close()
    except Exception as e:
        print(f"Noun addition failed: {e}")


# if __name__ == "__main__":
    #  # Add some users
    #  add_user("JohnDoe", "123456")

    #  # Add some words
    #  add_word("Haus", "House")
    #  add_word("Baum", "Tree")
    #  add_word("Wasser", "Water")

    #  # Log some exercises (Simulating user mistakes)
    #  log_exercise(1, 1, False)  # User 1 got 'Haus' wrong
    #  log_exercise(1, 2, True)   # User 1 got 'Baum' correct
    #  log_exercise(1, 1, False)  # User 1 got 'Haus' wrong again

    #  # Fetch difficult words
    #  print(get_difficult_words())
    # add_word("Bier", "Beer")
    # add_word("Handy", "Mobile phone")
    # log_exercise(user_id=1, word_id=5, correct=False)
    # update_difficulty(word_id=5, increase=True)
    # words = get_difficult_words(user_id=1, limit=3)

    # for word in words:
    #     print(f"Word: {word.word}, Difficulty: {word.difficulty}")


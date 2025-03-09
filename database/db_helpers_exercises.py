from database.db_models_exercises import Noun, NounExercise, Verb, VerbExercise
from database.db_models_general import SessionLocal, Vocabulary, User, Exercise

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

def log_verb_exercise(user_id, verb_id, correct):
    """Logs the user's verb conjugation attempt."""
    session = SessionLocal()
    new_exercise = VerbExercise(
        user_id=user_id, verb_id=verb_id, correct=correct)
    session.add(new_exercise)
    session.commit()
    session.close()


def log_noun_exercise(user_id, noun_id, correct):
    """Logs the user's noun article attempt."""
    session = SessionLocal()
    new_exercise = NounExercise(
        user_id=user_id, noun_id=noun_id, correct=correct)
    session.add(new_exercise)
    session.commit()
    session.close()


def get_difficult_verbs(limit=5):
    """Fetches verbs the user struggles with the most."""
    session = SessionLocal()
    verbs = (
        session.query(Verb.infinitive, Verb.past_simple, Verb.past_participle)
        .join(VerbExercise)
        .filter(VerbExercise.correct == False)
        .limit(limit)
        .all()
    )
    session.close()
    return verbs


def get_difficult_nouns(limit=5):
    """Fetches nouns where the user often picks the wrong article."""
    session = SessionLocal()
    nouns = (
        session.query(Noun.word, Noun.article)
        .join(NounExercise)
        .filter(NounExercise.correct == False)
        .limit(limit)
        .all()
    )
    session.close()
    return nouns


if __name__ == "__main__":
    # Add verbs
    add_verb("sehen", "sah", "gesehen")
    add_verb("gehen", "ging", "gegangen")

    # Add nouns
    add_noun("Tisch", "der")
    add_noun("Auto", "das")
    add_noun("Blume", "die")

    # Log exercises (Simulating mistakes)
    log_verb_exercise(1, 1, False)  # User 1 got 'sehen' wrong
    # User 1 picked the wrong article for 'Auto'
    log_noun_exercise(1, 2, False)

    # Fetch problem words
    print("Difficult Verbs:", get_difficult_verbs())
    print("Difficult Nouns:", get_difficult_nouns())

import random
from sqlalchemy import func
from database.db_models_exercises import Noun, NounExercise, Verb, VerbExercise
from database.db_models_general import Base, SessionLocal, Vocabulary, User, Exercise

def log_exercise(user_id, word_id, correct):
    """Logs the user's answer and updates difficulty for incorrect responses."""
    session = SessionLocal()

    # Log the exercise
    new_exercise = Exercise(user_id=user_id, word_id=word_id, correct=correct)
    session.add(new_exercise)

    if not correct:
        # Increase difficulty for incorrect words
        word = session.query(Vocabulary).filter(
            Vocabulary.id == word_id).first()
        if word:
            word.difficulty += 1

    session.commit()
    session.close()


def get_past_exercises(user_id, limit=5):
    """Fetches the last few exercises for a given user."""
    session = SessionLocal()
    exercises = (
        session.query(Exercise)
        .filter_by(user_id=user_id)
        .order_by(Exercise.timestamp.desc())
        .limit(limit)
        .all()
    )
    session.close()
    return exercises


def get_difficult_words(user_id, limit=5, difficulty_threshold=1):
    """Fetch words that the user struggles with."""
    session = SessionLocal()

    words = (
        session.query(Vocabulary)
        .filter(Vocabulary.difficulty >= difficulty_threshold)
        .order_by(Vocabulary.difficulty.desc())  # Prioritize hardest words
        .limit(limit)
        .all()
    )

    session.close()

    # If no difficult words are found, fall back to random words
    if not words:
        return get_random_words(limit)

    return words


def get_random_words(limit):
    return __get_random_from_table(Vocabulary, limit=limit)


def get_random_nouns(limit):
    return __get_random_from_table(Noun, limit=limit)


def get_random_verbs(limit):
    return __get_random_from_table(Verb, limit=limit)


def __get_random_from_table(table, limit=5):
    """Fetch random words if there are no difficult ones."""
    session = SessionLocal()
    words = session.query(table).order_by(func.random()).limit(limit).all()
    session.close()

    # Convert to list of dictionaries while excluding 'exercises'
    return [{col.name: getattr(word, col.name) for col in table.__table__.columns if col.name != "exercises"} for word in words]


def update_difficulty(word_id, correct):
    """Updates the difficulty of a word based on user response."""
    session = SessionLocal()
    word = session.query(Vocabulary).filter_by(id=word_id).first()

    if word:
        if correct:
            # Reduce difficulty if correct
            word.difficulty = max(0, word.difficulty - 1)
        else:
            word.difficulty += 1  # Increase difficulty if wrong
        session.commit()

    session.close()


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


def get_words_for_exercise(user_id, limit=5, difficulty_threshold=1, mix_ratio=0.3):
    """
    Fetches words for an exercise, prioritizing difficult words but mixing in some random ones.
    mix_ratio controls how many words will be selected randomly (default 30%).
    """
    session = SessionLocal()

    # Fetch difficult words
    difficult_words = (
        session.query(Vocabulary)
        .filter(Vocabulary.difficulty >= difficulty_threshold)
        .order_by(Vocabulary.difficulty.desc())  # Hardest words first
        .limit(int(limit * (1 - mix_ratio)))
        .all()
    )

    # Fetch random words to mix in
    random_words = (
        session.query(Vocabulary)
        .order_by(func.random())
        .limit(int(limit * mix_ratio))
        .all()
    )

    session.close()

    # Combine difficult and random words
    selected_words = difficult_words + random_words
    random.shuffle(selected_words)  # Shuffle so it's not predictable

    return selected_words

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
        session.query(Noun)
        .join(NounExercise)
        .filter(NounExercise.correct == False)
        .limit(limit)
        .all()
    )
    session.close()
    # Convert to list of dictionaries while excluding 'exercises'
    return [{col.name: getattr(noun, col.name) for col in Noun.__table__.columns if col.name != "exercises"} for noun in nouns]
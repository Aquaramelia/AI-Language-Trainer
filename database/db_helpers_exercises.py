import datetime
import random
import pandas as pd
from sqlalchemy import func
from database.db_models_exercises import NounArticlesRegular, NounArticleRegularExercise, Verb, VerbExercise, NounArticlesIrregular, NounArticleIrregularExercise, DateEntry
from database.db_models_general import SessionLocal, Vocabulary, Exercise

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


def get_random_nouns_regular_articles(limit):
    return __get_random_from_table(NounArticlesRegular, limit=limit)


def get_random_nouns_irregular_articles(limit):
    return __get_random_from_table(NounArticlesIrregular, limit=limit)


def get_random_verbs(limit):
    retrieved_verbs =  __get_random_from_table(Verb, limit=limit)
    if retrieved_verbs:
        return [(v["infinitive"], v["past_simple"], v["past_participle"]) for v in retrieved_verbs]


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
    log_date_entry(user_id=user_id)


def log_noun_regular_article_exercise(user_id, noun_id, correct):
    """Logs or updates the user's noun article attempt, adjusting difficulty."""
    session = SessionLocal()

    # Try to find an existing record for this user and noun
    existing_exercise = session.query(NounArticleRegularExercise).filter_by(user_id=user_id, noun_id=noun_id).first()

    if existing_exercise:
        # Update difficulty based on correctness
        if correct:
            existing_exercise.difficulty = max(0, existing_exercise.difficulty - 1)
        else:
            existing_exercise.difficulty += 1
    else:
        # Create new record with initial difficulty
        difficulty = 1 if not correct else 0
        new_exercise = NounArticleRegularExercise(user_id=user_id, noun_id=noun_id, difficulty=difficulty)
        session.add(new_exercise)

    session.commit()
    session.close()
    log_date_entry(user_id=user_id)
    
    
def log_noun_irregular_article_exercise(user_id, noun_id, correct):
    """Logs or updates the user's noun article attempt, adjusting difficulty."""
    session = SessionLocal()

    # Try to find an existing record for this user and noun
    existing_exercise = session.query(NounArticleIrregularExercise).filter_by(user_id=user_id, noun_id=noun_id).first()

    if existing_exercise:
        # Update difficulty based on correctness
        if correct:
            existing_exercise.difficulty = max(0, existing_exercise.difficulty - 1)
        else:
            existing_exercise.difficulty += 1
    else:
        # Create new record with initial difficulty
        difficulty = 1 if not correct else 0
        new_exercise = NounArticleIrregularExercise(user_id=user_id, noun_id=noun_id, difficulty=difficulty)
        session.add(new_exercise)
    session.commit()
    session.close()
    log_date_entry(user_id=user_id)

def log_date_entry(user_id, date=None):
    session = SessionLocal()
    todays_date = datetime.date.today()
    existing_date = session.query(DateEntry).filter_by(user_id=user_id, date=todays_date).first()
    if existing_date:
        existing_date.practice_count += 1
    else:
        practice_count = 1
        new_date_entry = DateEntry(user_id=user_id, date=todays_date, practice_count=practice_count)
        session.add(new_date_entry)
    session.commit()
    session.close()
    
def get_practice_data(user_id=1, start_date=None, end_date=None):
    session = SessionLocal()
    
    query = session.query(DateEntry).filter(DateEntry.user_id == user_id)
    
    # Apply date filters if provided
    if start_date:
        query = query.filter(DateEntry.date >= start_date)
    if end_date:
        query = query.filter(DateEntry.date <= end_date)

    # Fetch data
    data = query.all()
    session.close()
    print(data)  # Debugging step
    print([{"date": entry.date, "practice_count": entry.practice_count} for entry in data])

    df = pd.DataFrame({
        "date": [pd.Timestamp(entry.date) for entry in data],  # Convert to Timestamps
        "practice_count": [entry.practice_count for entry in data]  # Extract counts
    })



    return df


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


def get_difficult_vocabulary(limit=5):
    """Fetches nouns where the user often picks the wrong article."""
    session = SessionLocal()
    nouns = (
        session.query(NounArticlesRegular)
        .join(NounArticleRegularExercise)
        .filter(NounArticleRegularExercise.difficulty < 0)
        .limit(limit)
        .all()
    )
    session.close()
    # Convert to list of dictionaries while excluding 'exercises'
    return [{col.name: getattr(noun, col.name) for col in NounArticlesRegular.__table__.columns if col.name != "exercises"} for noun in nouns]


def get_difficult_regular_articles(limit=5):
    """Fetches nouns where the user often picks the wrong article."""
    session = SessionLocal()
    nouns = (
        session.query(NounArticlesRegular)
        .join(NounArticleRegularExercise)
        .filter(NounArticleRegularExercise.difficulty > 0)
        .limit(limit)
        .all()
    )
    session.close()
    # Convert to list of dictionaries while excluding 'exercises'
    return [{col.name: getattr(noun, col.name) for col in NounArticlesRegular.__table__.columns if col.name != "exercises"} for noun in nouns]


def get_difficult_irregular_articles(limit=5):
    """Fetches nouns where the user often picks the wrong article."""
    session = SessionLocal()
    nouns = (
        session.query(NounArticlesIrregular)
        .join(NounArticleIrregularExercise)
        .filter(NounArticleIrregularExercise.difficulty > 0)
        .limit(limit)
        .all()
    )
    session.close()
    # Convert to list of dictionaries while excluding 'exercises'
    return [{col.name: getattr(noun, col.name) for col in NounArticlesIrregular.__table__.columns if col.name != "exercises"} for noun in nouns]
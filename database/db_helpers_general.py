from database.db_models_general import SessionLocal, Vocabulary, User, Exercise


def add_user(username, password):
    """Adds a new user to the database."""
    session = SessionLocal()
    user = User(username=username, password=password)
    session.add(user)
    session.commit()
    session.close()


def add_word(word, translation):
    """Adds a new word to the vocabulary table."""
    session = SessionLocal()
    new_word = Vocabulary(word=word, translation=translation)
    session.add(new_word)
    session.commit()
    session.close()


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


def get_difficult_words(limit=5):
    """Fetches words the user struggles with the most."""
    session = SessionLocal()
    words = session.query(Vocabulary).order_by(
        Vocabulary.difficulty.desc()).limit(limit).all()
    session.close()
    return [(word.word, word.translation, word.difficulty) for word in words]


if __name__ == "__main__":
    # Add some users
    add_user("JohnDoe", "123456")

    # Add some words
    add_word("Haus", "House")
    add_word("Baum", "Tree")
    add_word("Wasser", "Water")

    # Log some exercises (Simulating user mistakes)
    log_exercise(1, 1, False)  # User 1 got 'Haus' wrong
    log_exercise(1, 2, True)   # User 1 got 'Baum' correct
    log_exercise(1, 1, False)  # User 1 got 'Haus' wrong again

    # Fetch difficult words
    print(get_difficult_words())

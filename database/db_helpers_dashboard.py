from sqlalchemy import desc, func
from sqlalchemy.orm import sessionmaker
from database.db_models_general import SessionLocal
from database.db_helpers_exercises import NounArticleRegularExercise, NounArticleIrregularExercise, NounArticlesIrregular, NounArticlesRegular, VerbExercise, Verb, Exercise, Vocabulary

def noun_article_statistics():
    # Create a session
    session = SessionLocal()

    # Number of explored nouns
    explored_regular = session.query(NounArticleRegularExercise.noun_id).distinct().count()
    explored_irregular = session.query(NounArticleIrregularExercise.noun_id).distinct().count()

    # Number of learnt nouns (difficulty = 0)
    learnt_regular = session.query(NounArticleRegularExercise).filter(NounArticleRegularExercise.difficulty == 0).count()
    learnt_irregular = session.query(NounArticleIrregularExercise).filter(NounArticleRegularExercise.difficulty == 0).count()

    # Number of nouns needing practice (difficulty > 0)
    practice_regular = session.query(NounArticleRegularExercise).filter(NounArticleRegularExercise.difficulty > 0).count()
    practice_irregular = session.query(NounArticleIrregularExercise).filter(NounArticleIrregularExercise.difficulty > 0).count()

    # Total count of exercises
    total_regular = session.query(NounArticlesRegular).count()
    total_irregular = session.query(NounArticlesIrregular).count()

    session.close()
    
    return {
        "explored_regular": explored_regular,
        "explored_irregular": explored_irregular,
        "learnt_regular": learnt_regular,
        "learnt_irregular": learnt_irregular,
        "practice_regular": practice_regular,
        "practice_irregular": practice_irregular,
        "total_regular": total_regular,
        "total_irregular": total_irregular
    }


def verb_tense_statistics():
    # Create a session
    session = SessionLocal()
    
    explored_verbs = session.query(VerbExercise.verb_id).distinct().count()
    
    learnt_verbs = session.query(VerbExercise).filter(VerbExercise.difficulty == 0).count()
    
    practice_verbs = session.query(VerbExercise).filter(VerbExercise.difficulty > 0).count()
    
    total_verbs = session.query(Verb).count()
    
    session.close()
    
    return {
        "explored_verbs": explored_verbs,
        "learnt_verbs": learnt_verbs,
        "practice_verbs": practice_verbs,
        "total_verbs": total_verbs
    }
    
def vocabulary_statistics(level):
    session = SessionLocal()
    explored_vocabulary = session.query(Exercise.word_id).filter(Exercise.level == level).distinct().count()
    learnt_vocabulary = session.query(Exercise).filter(Exercise.difficulty == 0).filter(Exercise.level == level).count()
    practice_vocabulary = session.query(Exercise).filter(Exercise.difficulty > 0).filter(Exercise.level == level).count()
    total_vocabulary = session.query(Vocabulary).filter(Vocabulary.level == level).count()
    
    session.close()
    
    return {
        "explored_vocabulary": explored_vocabulary,
        "learnt_vocabulary": learnt_vocabulary,
        "practice_vocabulary": practice_vocabulary,
        "total_vocabulary": total_vocabulary
    }
    
def most_practiced_levels():
    session = SessionLocal()
    levels = (
        session.query(Exercise.level)
        .group_by(Exercise.level)
        .order_by(desc(func.count(Exercise.id)))
        .limit(4)
        .all()
    )
    return levels
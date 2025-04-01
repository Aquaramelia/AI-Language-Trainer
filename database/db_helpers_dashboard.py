from sqlalchemy.orm import sessionmaker
from database.db_models_general import SessionLocal
from database.db_helpers_exercises import NounArticleRegularExercise, NounArticleIrregularExercise, NounArticlesIrregular, NounArticlesRegular

def noun_article_statistics():
    # Create a session
    session = SessionLocal()

    # Number of explored nouns
    explored_regular = session.query(NounArticleRegularExercise.noun_id).distinct().count()
    explored_irregular = session.query(NounArticleIrregularExercise.noun_id).distinct().count()

    # Number of learnt nouns (difficulty = 0)
    learnt_regular = session.query(NounArticleRegularExercise).filter_by(difficulty=0).count()
    learnt_irregular = session.query(NounArticleIrregularExercise).filter_by(difficulty=0).count()

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

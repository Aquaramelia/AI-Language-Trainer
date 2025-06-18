from dictionary_parsing.database_models import DictionaryEntry, CategoryEntry, SessionLocal


def get_category_all(category):
    session = SessionLocal()
    words = (
        session.query(CategoryEntry)
        .filter(CategoryEntry.category == category)
        .all()
    )
    session.close()
    return [{
        "word": entry.word,
        "article": entry.article,
        "forms": entry.forms,
        "senses": entry.senses,
        "glosses": entry.glosses,
        "examples": entry.examples,
        "derived": entry.derived,
        "related": entry.related,
        "antonyms": entry.antonyms,
        "hyponyms": entry.hyponyms,
        "synonyms": entry.synonyms
    } for entry in words]
    
def get_categories():
    session = SessionLocal()
    categories = (
        session.query(CategoryEntry.category)
        .distinct()
        .order_by(CategoryEntry.category)
        .all()
    )
    session.close()
    return [c[0] for c in categories]
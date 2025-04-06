import json
from google import genai
import os
from dotenv import load_dotenv

from database.db_helpers_exercises import get_difficult_verbs, get_random_nouns_regular_articles, get_random_nouns_irregular_articles, get_random_verbs, get_difficult_regular_articles, get_difficult_irregular_articles, get_vocabulary_words

load_dotenv()
API_KEY = os.environ["API_KEY"]


def generate_verb_exercise():
    """Generates a verb conjugation exercise using the user's weak verbs.
    If no weak verbs are found, or the weak verbs are fewer than the
    exercise limit, the rest are filled in with random verbs from the database."""
    limit = 10
    difficult_verbs = get_difficult_verbs(limit=limit)
    if not difficult_verbs:
        print("No weak verbs found. Getting random verbs!")
        difficult_verbs = get_random_verbs(limit=limit)
    else:
        difficult_verbs = list(set(difficult_verbs))
        if len(difficult_verbs) < limit:
            random_verbs = get_random_verbs(limit - len(difficult_verbs))
            difficult_verbs = difficult_verbs + random_verbs
    unique_verbs = list(set(difficult_verbs))
    # Format verbs for LLM prompt
    verb_list = "\n".join([f"{idx}: {infinitive} - {past_simple} - {past_participle}" 
                           for idx, (infinitive, past_simple, past_participle) in enumerate(unique_verbs, start=1)])


    question_prompt = f"""
    Generate a German verb conjugation exercise. Use the following irregular verbs:

    {verb_list}

    - Create fill-in-the-blank questions where the learner types the correct conjugated form of an irregular German verb.
    - The question format should be:
        -- (verb infinitive, required tense): Example sentence with blanks where the verb (and auxiliary, if needed) should be.
    - If an auxiliary verb is necessary (e.g., "habe gesehen"), include blanks for both.
    - Feel free to use a variety of grammatical tenses to widen the lerner's knowledge.
    - Feel free to use more advanced sentences.
    - Include the verb ID for tracking.
    - Provide the answer in valid JSON dictionary format.
    {{
        "questions": [
        {{
            "verb_id": 1,
            "infinitive: "gehen",
            "verb_tense": "Präteritum",
            "question": "Gestern ___ ich in den Park.",
            "correct_answer": "ging"
        }},
        {{
            "verb_id": 2,
            "infinitive": "sehen",
            "verb_tense": "Perfekt",
            "question": "Ich ___ den Film schon zweimal ___ .",
            "correct_answer": "habe, gesehen"
        }}
        ]
    }}

    """

    response = send_to_llm(question_prompt)
    return response


def generate_vocabulary_exercise(level):
    """Generates a noun article exercise using the user's weak vocabulary.
    If no weak vocabulary is found, or the weak words are fewer than the
    exercise limit, the rest are filled in with random words from the database, according to the selected level."""
    limit = 10
    difficult_words = get_vocabulary_words(limit=limit, level="a1.1", user_id=1)

    unique_words = list(set(difficult_words))
    print(unique_words)
    # Format nouns for LLM prompt
    noun_list = "\n".join([f"{id_} : {word}" for id_, word in unique_words])

    question_prompt = f"""
    Generate a German vocabulary exercise. Use the following nouns:

    {noun_list}

    - Create sentences where the learner picks the correct word for each sentence.
    - Include the noun ID for tracking.
    - Provide the answer in **valid JSON dictionary format**.
    - Example output:
      {{
          "questions": [
              {{
                  "noun_id": 1,
                  "question": "Ich habe gestern das ___ gefahren.",
                  "choices": ["Lampe", "Auto", "Handy"],
                  "correct_answer": "Auto"
              }},
              {{
                  "noun_id": 2,
                  "question": "Wo hast du mein ___ gelassen?",
                  "choices": ["Auto", "Lampe", "Handy"],
                  "correct_answer": "Handy"
              }}
          ]
      }}
    """
    # response = send_to_llm(question_prompt)
    
    response = {'questions': [{'noun_id': 527, 'question': 'Wir brauchten eine hohe ___, um die Wohnung zu mieten.', 'choices': ['Kaution', 'Kilo', 'Deutsch'], 'correct_answer': 'Kaution'}, {'noun_id': 302, 'question': 'Ich brauche ein ___ Mehl für den Kuchen.', 'choices': ['Adresse', 'Kilo', 'Projektor'], 'correct_answer': 'Kilo'}, {'noun_id': 14, 'question': 'Ich lerne seit einem Jahr ___.', 'choices': ['Wohnung', 'Deutsch', 'Problem'], 'correct_answer': 'Deutsch'}, {'noun_id': 189, 'question': 'Das ___ ist sehr hilfreich für das Lernen der Grammatik.', 'choices': ['Kursbuch', 'Computer', 'Kaution'], 'correct_answer': 'Kursbuch'}, {'noun_id': 211, 'question': 'Der ___ ist kaputt, wir können die Präsentation nicht zeigen.', 'choices': ['Projektor', 'Kilo', 'Adresse'], 'correct_answer': 'Projektor'}, {'noun_id': 392, 'question': 'Ich arbeite jeden Tag am ___.', 'choices': ['Computer', 'Wohnung', 'Problem'], 'correct_answer': 'Computer'}, {'noun_id': 85, 'question': 'Kannst du mir bitte deine ___ geben?', 'choices': ['Adresse', 'Kursbuch', 'Wann'], 'correct_answer': 'Adresse'}, {'noun_id': 452, 'question': 'Unsere ___ ist klein, aber gemütlich.', 'choices': ['Wohnung', 'Computer', 'Projektor'], 'correct_answer': 'Wohnung'}, {'noun_id': 210, 'question': 'Wir haben ein großes ___, das wir lösen müssen.', 'choices': ['Problem', 'Deutsch', 'Adresse'], 'correct_answer': 'Problem'}, {'noun_id': 451, 'question': '___ beginnt der Film?', 'choices': ['Wann', 'Kaution', 'Kilo'], 'correct_answer': 'Wann'}]}
    return response

def generate_noun_regular_article_exercise(limit=10):
    """Generates a noun article exercise using the user's weak nouns.
    If no weak nouns are found, or the weak nouns are fewer than the
    exercise limit, the rest are filled in with random nouns from the database."""
    difficult_nouns = get_difficult_regular_articles(limit=limit)

    if not difficult_nouns:
        print("No weak nouns found. Getting random nouns!")
        difficult_nouns = get_random_nouns_regular_articles(limit=limit)
    elif len(difficult_nouns) < limit:
        random_nouns = get_random_nouns_regular_articles(limit - len(difficult_nouns))
        difficult_nouns = difficult_nouns + random_nouns
    unique_nouns = [dict(t) for t in {tuple(d.items()) for d in difficult_nouns}]
    
    articles = ["der", "die", "das"]
    
    questions = []
    for noun in unique_nouns:
        correct_article = noun["article"]
        choices = articles
        
        question = {
            "noun_id": noun["id"],
            "question": f"What is the correct article for '{noun['word']}'?",
            "choices": choices,
            "correct_answer": correct_article
        }
        questions.append(question)

    return {"questions": questions}

def generate_noun_irregular_article_exercise(limit=10):
    """Generates a noun article exercise using the user's weak nouns.
    If no weak nouns are found, or the weak nouns are fewer than the
    exercise limit, the rest are filled in with random nouns from the database."""
    difficult_nouns = get_difficult_irregular_articles(limit=limit)

    if not difficult_nouns:
        print("No weak nouns found. Getting random nouns!")
        difficult_nouns = get_random_nouns_irregular_articles(limit=limit)
    elif len(difficult_nouns) < limit:
        random_nouns = get_random_nouns_irregular_articles(limit - len(difficult_nouns))
        difficult_nouns = difficult_nouns + random_nouns
    unique_nouns = [dict(t) for t in {tuple(d.items()) for d in difficult_nouns}]
    
    articles = ["der", "die", "das"]
    
    questions = []
    for noun in unique_nouns:
        correct_article = noun["article"]
        choices = articles
        
        question = {
            "noun_id": noun["id"],
            "noun": noun["word"],
            "question": f"What is the correct article for '{noun['word']}'?",
            "choices": choices,
            "correct_answer": correct_article
        }
        questions.append(question)

    return {"questions": questions}

def send_to_llm(prompt):
   # Call LLM
    client = genai.Client(api_key=API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    cleaned_response = response.text.strip("```json").strip("```").strip()

    try:
        exercise_data = json.loads(cleaned_response)
        return exercise_data  # Now it returns a dictionary
    except json.JSONDecodeError:
        return {"message": "Error: Could not parse exercise data."}
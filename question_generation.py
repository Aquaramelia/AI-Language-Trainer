import json
from google import genai
import os
from dotenv import load_dotenv

from database.db_helpers_exercises import get_difficult_nouns, get_difficult_verbs, get_random_nouns, get_random_verbs, get_random_words

load_dotenv()
API_KEY = os.environ["API_KEY"]


def generate_verb_exercise():
    """Generates a verb conjugation exercise using the user's weak verbs.
    If no weak verbs are found, or the weak verbs are fewer than the
    exercise limit, the rest are filled in with random verbs from the database."""
    limit = 10
    difficult_verbs = get_difficult_verbs(limit=limit)  # Get 3 weak verbs

    if not difficult_verbs:
        print("No weak verbs found. Getting random verbs!")
        difficult_verbs = get_random_verbs(limit=limit)
    elif len(difficult_verbs) < limit:
        random_verbs = get_random_verbs(limit - len(difficult_verbs))
        difficult_verbs = difficult_verbs + random_verbs
    unique_verbs = [dict(t) for t in {tuple(d.items()) for d in difficult_verbs}]
    # Format verbs for LLM prompt
    verb_list = "\n".join([f"{n['id']}: {n['infinitive']} - {n['past_simple']} - {n['past_participle']}" for n in unique_verbs])

    question_prompt = f"""
    Generate a German verb conjugation exercise. Use the following irregular verbs:

    {verb_list}

    - Create fill-in-the-blank questions where the learner types the correct conjugated form of an irregular German verb.
    - The question format should be:
        -- (verb infinitive, required tense): Example sentence with blanks where the verb (and auxiliary, if needed) should be.
    - If an auxiliary verb is necessary (e.g., "habe gesehen"), include blanks for both.
    - Include the verb ID for tracking.
    - Provide the answer in valid JSON dictionary format.
    {{
        "questions": [
        {{
            "verb_id": 1,
            "question": "gehen, past simple: Gestern ___ ich in den Park.",
            "correct_answer": "ging"
        }},
        {{
            "verb_id": 2,
            "question": "sehen, past participle: Ich ___ den Film schon zweimal ___ .",
            "correct_answer": "habe, gesehen"
        }}
        ]
    }}

    """

    response = send_to_llm(question_prompt)
    return response


def generate_noun_exercise():
    """Generates a noun article exercise using the user's weak nouns.
    If no weak nouns are found, or the weak nouns are fewer than the
    exercise limit, the rest are filled in with random nouns from the database."""
    limit = 10
    difficult_nouns = get_difficult_nouns(limit=limit)  # Get 3 weak verbs

    if not difficult_nouns:
        print("No weak nouns found. Getting random nouns!")
        difficult_nouns = get_random_nouns(limit=limit)
    elif len(difficult_nouns) < limit:
        random_nouns = get_random_nouns(limit - len(difficult_nouns))
        difficult_nouns = difficult_nouns + random_nouns
    unique_nouns = [dict(t) for t in {tuple(d.items()) for d in difficult_nouns}]
    # Format nouns for LLM prompt
    noun_list = "\n".join([f"{n['id']}: {n['word']} - {n['article']}" for n in unique_nouns])

    question_prompt = f"""
    Generate a German noun article exercise. Use the following nouns:

    {noun_list}

    - Create **multiple-choice questions** where the learner picks the correct article.
    - Include the noun ID for tracking.
    - Provide the answer in **valid JSON dictionary format**.
    - Example output:
      {{
          "questions": [
              {{
                  "noun_id": 1,
                  "question": "What is the correct article for 'Auto'?",
                  "choices": ["der", "die", "das"],
                  "correct_answer": "das"
              }},
              {{
                  "noun_id": 2,
                  "question": "What is the correct article for 'Lampe'?",
                  "choices": ["der", "die", "das"],
                  "correct_answer": "die"
              }}
          ]
      }}
    """
    response = send_to_llm(question_prompt)
    return response


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
import json
from google import genai
import os
from dotenv import load_dotenv

from database.db_helpers_exercises import get_difficult_nouns, get_difficult_verbs

load_dotenv()
API_KEY = os.environ["API_KEY"]


def generate_verb_exercise():
    """Generates a verb conjugation exercise using the user's weak verbs."""
    difficult_verbs = get_difficult_verbs(2)  # Get 3 weak verbs

    if not difficult_verbs:
        return "No weak verbs found. Try more exercises!"

    # Format verbs for LLM prompt
    verb_list = "\n".join(
        [f"{v[0]} - {v[1]} - {v[2]}" for v in difficult_verbs])

    question_prompt = f"""
    Generate a German verb conjugation exercise. Use the following irregular verbs:

    {verb_list}

    - Create **one fill-in-the-blank sentence** per verb.
    - Include the correct answer in a JSON format.
    - Example output:
      {{
          "questions": [
              {{
                  "sentence": "Gestern ___ ich einen Film. (sehen)",
                  "answer": "sah"
              }},
              {{
                  "sentence": "Letzte Woche ___ wir nach Berlin. (gehen)",
                  "answer": "gingen"
              }}
          ]
      }}
    """

    # Call LLM
    client = genai.Client(api_key=API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=question_prompt
    )

    return response.text  # Return JSON-formatted exercises


def generate_noun_exercise():
    """Generates a noun article exercise using the user's weak nouns."""
    difficult_nouns = get_difficult_nouns(3)  # Get 3 weak nouns

    if not difficult_nouns:
        return "No weak nouns found. Try more exercises!"

    # Format nouns for LLM prompt
    noun_list = "\n".join([f"{n[0]} - {n[1]}" for n in difficult_nouns])

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
                  "options": ["der", "die", "das"],
                  "answer": "das"
              }},
              {{
                  "noun_id": 2,
                  "question": "What is the correct article for 'Lampe'?",
                  "options": ["der", "die", "das"],
                  "answer": "die"
              }}
          ]
      }}
    """

    # Call LLM
    client = genai.Client(api_key=API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=question_prompt
    )
    cleaned_response = response.text.strip("```json").strip("```").strip()

    try:
        exercise_data = json.loads(cleaned_response)
        return exercise_data  # Now it returns a dictionary
    except json.JSONDecodeError:
        return {"message": "Error: Could not parse exercise data."}


print(generate_verb_exercise())
print(generate_noun_exercise())

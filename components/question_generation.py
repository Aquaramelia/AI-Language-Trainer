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

    response = send_to_llm_decode_json(question_prompt)
    return response


def generate_vocabulary_exercise(level):
    """Generates a noun article exercise using the user's weak vocabulary.
    If no weak vocabulary is found, or the weak words are fewer than the
    exercise limit, the rest are filled in with random words from the database, according to the selected level."""
    limit = 10
    difficult_words = get_vocabulary_words(limit=limit, level=level, user_id=1)

    unique_words = list(set(difficult_words))
    # Format nouns for LLM prompt
    noun_list = "\n".join([f"{id_} : {word}" for id_, word in unique_words])

    question_prompt = f"""
    Generate a German vocabulary exercise. Use the following words:

    {noun_list}

    - Create sentences where the learner picks the correct word for each sentence from the given pool of words.
    - Include the word ID for tracking.
    - Provide the answer in **valid JSON dictionary format**.
    - In case of a verb, change it to the correct verb tense form in the choices and the correct answer.
    - Example output:
      {{
          "questions": [
              {{
                  "word_id": 1,
                  "question": "Ich habe gestern das ___ gefahren.",
                  "correct_answer": "Auto"
              }},
              {{
                  "word_id": 2,
                  "question": "Wo hast du mein ___ gelassen?",
                  "correct_answer": "Handy"
              }},
              {{
                  "word_id": 3,
                  "question": "Ist die ___ an?",
                  "correct_answer": "Lampe"
              }}
          ],
          "choices": ["Auto", "Lampe", "Handy"]
      }}
    """
    response = send_to_llm_decode_json(question_prompt)
    # print(response)
    # response = {'questions': [{'word_id': 2, 'question': 'Ist ___ in Ordnung?', 'correct_answer': 'alles'}, {'word_id': 143, 'question': 'Darf ich mich Ihnen ___?', 'correct_answer': 'vorstellen'}, 
# {'word_id': 410, 'question': 'Das Essen ist sehr ___. ', 'correct_answer': 'lecker'}, {'word_id': 445, 'question': 'Wir treffen uns ___ 10 Uhr.', 'correct_answer': 'um'}, {'word_id': 
# 472, 'question': 'Das ist sehr ___. Ich kaufe es!', 'correct_answer': 'billig'}, {'word_id': 167, 'question': 'Hier ist unser ___.', 'correct_answer': 'Familienfoto'}, {'word_id': 113, 'question': 'Ich möchte ___ nach Hause gehen.', 'correct_answer': 'jetzt'}, {'word_id': 387, 'question': 'Der Kurs ___ morgen.', 'correct_answer': 'beginnt'}, {'word_id': 260, 'question': 'Ich ___ ein neues Auto.', 'correct_answer': 'brauche'}, {'word_id': 389, 'question': 'Ich gehe ins ___, um zu schlafen.', 'correct_answer': 'Bett'}], 'choices': ['alles', 'vorstellen', 'lecker', 'um', 'billig', 'Familienfoto', 'jetzt', 'beginnt', 'brauche', 'Bett']}
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

def generate_writing_exercise():
    question_prompt = """ 
    Create a list of 5 essay or short writing prompts suitable for A1-C1 level German learners. The topics should be engaging, encouraging students to express their opinions and reflect on personal experiences. Each prompt should be clear and straightforward, allowing for creative responses. The prompts should vary in style, with some focusing on personal experience, while others encourage opinion-based writing. Provide the title of the prompt and a brief description to explain the writing task. Output in a **valid JSON format** as follows:
    {
        "writing_prompts": [
            {
                "prompt": "Beschreibe deinen letzten Urlaub. Wo bist du hingefahren und was hast du dort gemacht?",
                "level": "A1"
            },
            {
                "prompt": "Was sind deine Hobbys und warum machst du sie gerne? Erkläre, was dir an deinen Hobbys am meisten Spaß macht.",
                "level": "A2"
            },
            {
                "prompt": "Stell dir vor, du könntest einen Tag lang jemand anderes sein. Wer würdest du sein und was würdest du an diesem Tag tun?",
                "level": "B1"
            },
            {
                "prompt": "Was denkst du über den Klimawandel? Welche Maßnahmen sollten deiner Meinung nach ergriffen werden, um die Umwelt zu schützen?",
                "level": "B2"
            },
            {
                "prompt": "Was sind die wichtigsten Eigenschaften einer guten Freundschaft? Erkläre, was du von deinen Freunden erwartest und was eine Freundschaft für dich bedeutet.",
                "level": "C1"
            }
        ]
    }
    """
    # response = send_to_llm(prompt=question_prompt)
    # print(response)
    response = {'writing_prompts': [{'title': 'Meine perfekte Reise: Ein Traumziel', 'prompt': 'Stell dir vor, du könntest eine perfekte Reise planen, ohne Einschränkungen beim Budget. Wohin würdest du reisen, warum genau dorthin und was würdest du dort alles erleben? Beschreibe deine ideale Reiseroute und begründe deine Entscheidungen.', 'description': 'This prompt encourages students to use their imagination and vocabulary related to travel, culture, and personal preferences. They should describe their dream destination and explain their reasons for choosing it.', 'level': 'B1'}, {'title': 'Die Bedeutung von Technologie in meinem Leben', 'prompt': 'Wie hat Technologie dein Leben in den letzten Jahren beeinflusst? Welche Vorteile und Nachteile siehst du? Beschreibe ein Beispiel, in dem Technologie dir geholfen oder Probleme verursacht hat. Was denkst du über die zukünftige Rolle der Technologie?', 'description': 'This prompt asks students to reflect on the impact of technology on their lives, both positive and negative. It encourages critical thinking and the expression of personal opinions.', 'level': 'B1'}, {'title': 'Ein unvergessliches Erlebnis', 'prompt': 'Erzähle von einem unvergesslichen Erlebnis in deinem Leben. Was ist passiert, wer war dabei und warum war es so besonders für dich? Welche Lehren hast du daraus gezogen?', 'description': 'This prompt focuses on personal narrative and encourages students to use descriptive language to recount a significant experience and reflect on its meaning.', 'level': 'B1', 'type': 'narrative'}, {'title': 'Sollte Schuluniform Pflicht sein?', 'prompt': 'In vielen Ländern gibt es eine Debatte darüber, ob Schuluniformen Pflicht sein sollten oder nicht. Was ist deine Meinung dazu? Welche Argumente gibt es dafür und dagegen? Begründe deine Position.', 'description': 'This prompt is designed to elicit opinion-based writing and encourages students to develop arguments for or against school uniforms. It requires them to consider different perspectives and provide reasoned justifications.', 'level': 'B2'}, {'title': 'Meine Vorbilder und ihre Bedeutung', 'prompt': 'Wer sind deine Vorbilder und warum bewunderst du sie? Was kannst du von ihnen lernen? Beschreibe, wie diese Personen dich beeinflusst haben und welche Eigenschaften du an ihnen besonders schätzt.', 'description': 'This prompt encourages students to reflect on their values and the people who inspire them. It prompts them to analyze the qualities they admire in others and how these qualities have influenced their own lives.', 'level': 'B2'}]}
    return response

def correct_writing_exercise(prompt, answer):
    llm_prompt = f""" {{
        "correction_prompt": {{
            "writing_prompt": {prompt},
            "student_answer": {answer},
            "instructions": "Bitte korrigiere die folgenden Fehler in der Antwort des Schülers. Achte auf Grammatik, Wortschatz und Satzstruktur. Gebe dem Schüler eine Punktzahl von 0 bis 10 basierend auf der Qualität der Antwort.",
            "scoring_guidelines": {{
                "0-2": "Schwierige Fehler, schwer verständlich oder unvollständige Antwort.",
                "3-5": "Einige Fehler, aber die Antwort ist größtenteils verständlich.",
                "6-8": "Geringe Fehler, Antwort ist klar und gut strukturiert.",
                "9-10": "Nahezu fehlerfrei, sehr gute Struktur und Ausdruck."
            }}
        }}
        }}
    """
    # response = send_to_llm(llm_prompt)
    # print(response)
    response = """ Okay, hier ist eine korrigierte Version der Schülerantwort, eine Bewertung und eine Begründung dafür:\n\n**Korrigierte Antwort:**\n\n*   "Technologie hat mein Leben in den letzten Jahren stark beeinflusst. Einer der größten Vorteile ist die Möglichkeit der schnellen Kommunikation mit Menschen weltweit. Soziale Medien und Messaging-Dienste ermöglichen ständigen Kontakt, was besonders auf Reisen oder während der Pandemie hilfreich war. Ein weiterer Vorteil ist die Effizienzsteigerung bei Aufgaben wie Online-Shopping oder der Nutzung digitaler Organisationstools.\n\nAuf der anderen Seite gibt es auch Nachteile. Die ständige Erreichbarkeit kann 
stressig sein, und ich fühle mich manchmal von meinem Smartphone abhängig. Ein Beispiel für die positiven Auswirkungen von Technologie ist das Erlernen neuer Fähigkeiten durch Online-Kurse, was meine Karriere gefördert hat. Schwierigkeiten entstanden jedoch, wenn ich zu viel Zeit vor dem Laptop verbrachte und mich dadurch weniger bewegte.\n\nIch gehe davon aus, dass Technologie in Zukunft noch stärker in unseren Alltag integriert 
sein wird. Sie wird unser Leben vereinfachen und effizienter gestalten, aber wir müssen auf eine gesunde Balance achten, um negative Auswirkungen zu minimieren."\n\n**Bewertung: 4/10**\n\n**Begründung:**\n\nDie Antwort des Schülers geht am Thema vorbei. Die Aufgabe war es, eine Traumreise zu beschreiben, aber der Schüler hat stattdessen über die Auswirkungen von Technologie geschrieben. Die Antwort ist zwar kohärent und grammatikalisch korrekt, aber sie erfüllt die Aufgabe nicht. Dies deutet darauf hin, dass der Schüler entweder die Aufgabe missverstanden hat oder eine vorgefertigte Antwort verwendet hat. Daher ist die Bewertung niedrig, da die inhaltliche Relevanz zur Aufgabenstellung vollständig fehlt. Die korrigierte Version hat zwar die Grammatik und den Ausdruck verbessert, ändert aber nichts an der Tatsache, dass die Antwort nicht auf die Frage eingeht. """
    # return response.text
    return response

def send_to_llm_decode_json(prompt):
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
    
def send_to_llm(prompt):
   # Call LLM
    client = genai.Client(api_key=API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    return response
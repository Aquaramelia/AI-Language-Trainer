import requests


def __translate_word(word, source_lang, target_lang):
    """Fetches a translation for a given word."""
    url = "https://deep-translator-api.azurewebsites.net/google/"  # Example, may require API key
    params = {
        "source": source_lang,
        "target": target_lang,
        "text": word,
        "proxies": []
    }
    
    response = requests.post(url, json=params)

    if response.status_code == 200:
        return response.json().get("translation", "Translation not found")
    else:
        return "Error: Unable to fetch translation" + response.text

def translate_to_english(word):
   return __translate_word(word, "german", "english")

def translate_to_german(word):
   return __translate_word(word, "english", "german")
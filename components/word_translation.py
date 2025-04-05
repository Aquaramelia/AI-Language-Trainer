from googletrans import Translator
from st_helpers.asyncio_helpers import run_async_task

translator = Translator()


async def translate(text, src, dest):
    # Directly await the async translation call
    translation = await translator.translate(text, src=src, dest=dest)
    return translation.text


def translate_to_english(word):
    try:
        result = run_async_task(translate, word, "de", "en")
        return result
    except:
        return None


def translate_to_german(word):
    return run_async_task(translate, word, "en", "de")

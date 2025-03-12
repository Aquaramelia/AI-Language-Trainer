import streamlit as st
from word_translation import translate_to_english, translate_to_german

st.set_page_config(page_title="Home - AI Language Trainer", page_icon="📖")
st.title("Welcome to the Language Trainer! 🇩🇪")

st.sidebar.success("Select a page above to start training! 👆")

# Sidebar interface for translation
st.sidebar.header("Translation Tool")

# Define callback functions
def go_to_translation_english():
    user_input = st.session_state.get("button_en_translation", "")
    if user_input:
        st.session_state.translation_en = translate_to_english(user_input)

def go_to_translation_german():
    user_input = st.session_state.get("button_de_translation", "")
    if user_input:
        st.session_state.translation_de = translate_to_german(user_input)

# German -> English Input Box
st.sidebar.text_input(
    label="German -> English:",
    key="button_en_translation",
    label_visibility="visible",
    max_chars=50,
    on_change=go_to_translation_english
)

translation_text_en = st.session_state.get("translation_en", "")
st.sidebar.write(
    f"Translation: {translation_text_en}" if translation_text_en else "")

# English -> German Input Box
st.sidebar.text_input(
    label="English -> German:",
    key="button_de_translation",
    label_visibility="visible",
    max_chars=50,
    on_change=go_to_translation_german
)

translation_text_de = st.session_state.get("translation_de", "")
st.sidebar.write(
    f"Translation: {translation_text_de}" if translation_text_de else "")
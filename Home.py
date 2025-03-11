import streamlit as st
from word_translation import translate_to_english, translate_to_german

st.set_page_config(page_title="Home - AI Language Trainer", page_icon="📖")
st.title("Welcome to the Language Trainer! 🇩🇪")

st.sidebar.success("Select a page above to start training! 👆")

# Sidebar interface for translation
st.sidebar.header("Translation Tool")

# Create a text box for the user to input an unknown word
en_word_to_translate = st.sidebar.text_input("Enter a word in german:", key="button_en_tranlation", label_visibility="hidden")

# Create a button to trigger the translation
if st.sidebar.button("English translation"):
    if en_word_to_translate:
        en_translation = translate_to_english(en_word_to_translate)
        st.sidebar.write(f"Translation: {en_translation}")
    else:
        st.sidebar.write("Please enter a word to translate.")
        

# Create a text box for the user to input an unknown word
de_word_to_translate = st.sidebar.text_input("Enter a word in english:", key="button_de_tranlation", label_visibility="hidden")

# Create a button to trigger the translation
if st.sidebar.button("German translation"):
    if de_word_to_translate:
        de_translation = translate_to_german(de_word_to_translate)
        st.sidebar.write(f"Translation: {de_translation}")
    else:
        st.sidebar.write("Please enter a word to translate.")
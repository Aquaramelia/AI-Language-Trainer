import streamlit as st
from st_helpers.static_file_helpers import move_font_files

def set_background(image_url="https://www.transparenttextures.com/patterns/debut-light.png"):
    css = f"""
    <style>
        html, body, .stApp {{
            background-color: transparent;
            background-image: url({image_url}), linear-gradient(62deg, rgb(19, 109, 198) 0%, rgb(181, 108, 255) 100%);
            background-repeat: repeat;
        }}

        h1 {{
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    
def load_css(css_file_name="styles.css"):
    move_font_files()
    with open(css_file_name, "r") as f:
        css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        
def complete_sentence(question_data):
    """Fills in the blanks of a sentence with the correct answers."""
    sentence = question_data["question"]
    answers = question_data["correct_answer"].split(", ")
    
    # Split the sentence at blanks while preserving separators
    parts = sentence.split("___")

    # Reconstruct the sentence, inserting answers only where available
    completed_sentence = "".join(part + (answers[i] if i < len(answers) else "") for i, part in enumerate(parts))

    return completed_sentence

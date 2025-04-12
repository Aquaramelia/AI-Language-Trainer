from ast import literal_eval
import streamlit as st

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

def safe_join(value):
    """
    Converts a value to a comma-separated string if it's a list or a string representing a list.
    """
    # If it's a list already, join its string representations.
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    # If it's a string, try parsing it to a list.
    elif isinstance(value, str):
        try:
            parsed = literal_eval(value)
            if isinstance(parsed, list):
                return ", ".join(str(item) for item in parsed)
            else:
                return value
        except Exception:
            return value
    else:
        return str(value)
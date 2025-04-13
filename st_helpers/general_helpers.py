from ast import literal_eval
import pandas as pd
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

def safe_join(value, delimiter=", ", limit=None):
    """
    Converts a value to a comma-separated string if it's a list or a string representing a list.
    """
    # If it's a list already, join its string representations.
    if isinstance(value, list):
        return delimiter.join(str(item) for item in value)
    # If it's a string, try parsing it to a list.
    elif isinstance(value, str):
        try:
            parsed = literal_eval(value)
            if isinstance(parsed, list):
                joined = delimiter.join(str(item) for item in parsed)
                print(joined)
                if limit:
                    return joined if len(joined) <= limit else joined[:limit].rsplit(" ", 1)[0] + "…"
                else:
                    return joined
            else:
                return value
        except Exception:
            return value
    else:
        return str(value)
    
    
def safe_bullets(value, limit=None):
    """
    Converts a value to a bullet-point list in Markdown format.
    
    Args:
        value (str or list): A list or string representing a list.
        limit (int, optional): Character limit for the entire result.
    
    Returns:
        str: Markdown-style bullet list as a string.
    """
    def truncate(text, limit):
        return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + "…"

    if isinstance(value, list):
        bullets = "\n".join(f"- {str(item)}" for item in value)
        return truncate(bullets, limit) if limit else bullets

    elif isinstance(value, str):
        try:
            parsed = literal_eval(value)
            if isinstance(parsed, list):
                bullets = "\n".join(f"- {str(item)}" for item in parsed)
                return truncate(bullets, limit) if limit else bullets
            else:
                return f"- {value}"
        except Exception:
            return f"- {value}"
    else:
        return f"- {str(value)}"
    
    
def safe_table_cell(value, limit=None):
    """
    Converts a value to a newline-separated string for use in a st.table cell.
    
    Args:
        value (str or list): A list or a string representing a list.
        limit (int, optional): Character limit for the entire result.
    
    Returns:
        str: Newline-separated string suitable for st.table.
    """
    def truncate(text, limit):
        return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + "…"

    if isinstance(value, list):
        text = "\n".join(str(item) for item in value)
        return truncate(text, limit) if limit else text

    elif isinstance(value, str):
        try:
            parsed = literal_eval(value)
            if isinstance(parsed, list):
                text = "\n".join(str(item) for item in parsed)
                words_str = truncate(text, limit) if limit else text
                words_list = words_str.split()
                df = pd.DataFrame(words_list, columns=["Forms"])
                return df
            else:
                return str(value)
        except Exception:
            return str(value)
    else:
        return str(value)
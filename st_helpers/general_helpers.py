import streamlit as st

def set_background(image_url="https://www.transparenttextures.com/patterns/debut-light.png"):
    css = f"""
    <style>
        .stApp {{
            background-image: url("{image_url}");
            background-color: #5b4189;
        }}

        .stApp header {{
            background-image: url("{image_url}");
            background-color: #5b4189;
        }}
        
        h1 {{
           text-shadow: 2px;
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

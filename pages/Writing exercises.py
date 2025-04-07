import streamlit as st
from components.question_generation import generate_writing_exercise, correct_writing_exercise
from st_helpers.general_helpers import set_background, load_css
from components.word_translation import translate_to_english
from streamlit_input_box import input_box

st.set_page_config(
    page_title="Writing Exercises - AI Language Trainer", 
    page_icon="📖",
    layout="wide")
set_background()
load_css()
st.title("Writing Exercises")
st.header("Practice your writing skills!")
st.divider()

def refresh_test():
    st.session_state.questions = generate_writing_exercise()
    questions = st.session_state.questions["writing_prompts"]
    st.rerun()
    
USER_ID = 1

if "questions" not in st.session_state:
    st.session_state.questions = generate_writing_exercise()
    st.session_state.llm_called = True
else:
    st.session_state.llm_called = False
questions = st.session_state.questions["writing_prompts"]

def display_question():
    print(question for question in questions)
    
    
tabs = [f"Level {question['level']}" for question in questions]

# Create tabs dynamically
tab_objs = st.tabs(tabs)

# Display prompts for each tab
for i, tab in enumerate(tab_objs):
    with tab:
        with st.container(
            key=f"question-container-{i}"
        ):
            st.header(questions[i]["title"])
            col1, col2, col3 = st.columns([1,5,1])
            with col2:
                st.markdown(f'<div class="notepad"><div class="top"></div><div class="paper">{questions[i]["prompt"]}</div></div><br/>', unsafe_allow_html=True)
                answer = st.text_area(
                    key=f"textarea-{i}",
                    label="Hier kannst du deine Antwort eingeben:",
                    height=800
                    )
            col1, col2, col3 = st.columns([1,1,1])
            response = ""
            with col2:
                if st.button(
                    label="Submit my answer!",
                    key=f"submit-button-{i}",
                    use_container_width=True):
                    response = correct_writing_exercise(questions[i]["prompt"], answer)
            if response:
                with st.chat_message("ai"):
                    st.write(response)
                    

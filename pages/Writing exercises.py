import streamlit as st
from components.question_generation import generate_writing_exercise, correct_writing_exercise
from st_helpers.general_helpers import set_background, load_css
from database.db_helpers_exercises import log_writing_exercise, log_date_entry, get_writing_topics, save_new_writing_topics

st.set_page_config(
    page_title="Writing Exercises - AI Language Trainer", 
    page_icon="📖",
    layout="wide")
set_background()
load_css()
st.title("Writing Exercises")
st.header("Practice your writing skills!")
USER_ID = 1

def refresh_test():
    questions = get_writing_topics(USER_ID)
    if not questions:
        questions = generate_writing_exercise()
        save_new_writing_topics(USER_ID, questions["writing_prompts"])
        questions = questions["writing_prompts"]
    st.session_state.questions = questions
    st.session_state.disabled = {idx: False for idx in range(len(questions))}
    st.session_state.translation = {idx: False for idx in range(len(questions))}
    st.session_state.response = {idx: None for idx in range(len(questions))}
    st.session_state.llm_in_progress = None
    st.rerun()

def get_new_topics():
    questions = generate_writing_exercise()
    save_new_writing_topics(USER_ID, questions["writing_prompts"])
    questions = questions["writing_prompts"]
    st.session_state.questions = questions
    st.session_state.disabled = {idx: False for idx in range(len(questions))}
    st.session_state.translation = {idx: False for idx in range(len(questions))}
    st.session_state.response = {idx: None for idx in range(len(questions))}
    st.rerun()

if "session_mode" not in st.session_state or st.session_state.session_mode != "writing_exercises":
    st.session_state.session_mode = "writing_exercises"
    refresh_test()

if "questions" not in st.session_state:
    questions = get_writing_topics(USER_ID)
    if not questions:
        questions = generate_writing_exercise()
        save_new_writing_topics(USER_ID, questions["writing_prompts"])
        st.session_state.questions = questions["writing_prompts"]
        st.session_state.llm_called = True
else:
    st.session_state.llm_called = False

questions = st.session_state.questions

if "disabled" not in st.session_state:
    st.session_state.disabled = {idx: False for idx in range(len(questions))}

if "translation" not in st.session_state:
    st.session_state.translation = {idx: False for idx in range(len(questions))}

if "response" not in st.session_state:
    st.session_state.response = {idx: None for idx in range(len(questions))}

if "llm_in_progress" not in st.session_state:
    st.session_state.llm_in_progress = None

col1, col2, col3 = st.columns([1,2,1])

generation_button_key = "generate-topics-button"
if generation_button_key in st.session_state and st.session_state[generation_button_key] == True:
    st.session_state.llm_in_progress = True
else:
    st.session_state.llm_in_progress = False
with col2:
    if st.button(
        key=generation_button_key,
        label="Generate new topics! 🔮",
        disabled=st.session_state.llm_in_progress,
        use_container_width=True
    ):
        st.session_state.llm_in_progress = True
        get_new_topics()
        st.session_state.llm_in_progress = False
        st.rerun()
        
st.divider()
    
    
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
            colA, colB, colC = st.columns([1,5,1])
            with colB:
                st.markdown(f'<div class="notepad"><div class="top"></div><div class="paper" id="essay-prompt">{questions[i]["prompt"]}</div></div><br/>', unsafe_allow_html=True)
                answer = st.text_area(
                    key=f"textarea-{i}",
                    label="Hier kannst du deine Antwort eingeben:",
                    height=800,
                    value=questions[i].get("answer", None)
                    )
            colX, colY, colZ = st.columns([1,1,1])
            response = st.session_state.response[i]
            with colY:
                if st.button(
                    label="Save progress",
                    key=f"save-progress-button-{i}",
                    use_container_width=True,
                    disabled=st.session_state.disabled[i]):
                    log_writing_exercise(
                        user_id=USER_ID,
                        title=questions[i]["title"],
                        prompt=questions[i]["prompt"],
                        level=questions[i]["level"],
                        answer=answer,
                        correction=response
                    )
                if st.button(
                    label="Submit my answer!",
                    key=f"submit-button-{i}",
                    use_container_width=True,
                    disabled=st.session_state.disabled[i]):
                    response = correct_writing_exercise(questions[i]["prompt"], answer)
                    log_writing_exercise(
                        user_id=USER_ID,
                        title=questions[i]["title"],
                        prompt=questions[i]["prompt"],
                        level=questions[i]["level"],
                        answer=answer,
                        correction=response
                    )
                    log_date_entry(
                        user_id=USER_ID
                    )
                    st.session_state.response[i] = response
                    st.session_state.disabled[i] = True
                    st.rerun()
                
            colD, colE, colG = st.columns([1,8,1])
            with colE:
                with st.container(
                    key=f"response-container-{i}"
                ):
                    if response:
                        with st.chat_message(
                            name="ai",
                            avatar="🐤"):
                            st.write(response)
            st.markdown("\n\n")
                    

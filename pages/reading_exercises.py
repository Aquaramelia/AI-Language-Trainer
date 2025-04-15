import random
import streamlit as st
from database.db_helpers_exercises import log_reading_exercise
from components.question_generation import generate_reading_exercise
from st_helpers.general_helpers import set_background, load_css
from st_helpers.reading_helpers import available_modes

set_background()
load_css()

st.title("Reading Exercises")
st.header("Practice your reading comprehension by answering the questions.")

mode_container = st.container(key="stButtonGroup-container-mode")
with mode_container:
    current_mode = st.segmented_control(
        label="Reading level:", 
        label_visibility="collapsed", 
        options=list(available_modes.keys()), 
        default="Level: A1",
        )
    
st.divider()

def refresh_test():
    # Reset only necessary session state variables
    if "session_mode" in st.session_state:
        st.session_state.questions = generate_reading_exercise(st.session_state.session_mode)
        questions = st.session_state.questions["reading_exercise"]
    st.session_state.score = 0
    st.session_state.answers = {idx: None for idx in range(len(questions["questions"]))}
    st.session_state.disabled = {idx: False for idx in range(len(questions["questions"]))}
    st.session_state.is_correct = {idx: None for idx in range(len(questions["questions"]))}
    st.session_state.answers_checked = {idx: False for idx in range(len(questions["questions"]))}
    st.session_state.test_complete = False
    st.session_state.icons = {}
    
    # Re-run the script to update UI without full reload
    st.rerun()

USER_ID = 1  # Placeholder for session

if "session_mode" not in st.session_state or st.session_state.session_mode not in available_modes.values():
    st.session_state.session_mode = "a1"
    refresh_test()
    
if current_mode and available_modes[current_mode] != st.session_state.session_mode:
    st.session_state.session_mode = available_modes[current_mode]
    refresh_test()
    
if "questions" not in st.session_state:
    st.questions = generate_reading_exercise(st.session_state.session_mode)
    st.session_state.llm_called = True
else:
    st.session_state.llm_called = False
    
questions = st.session_state.questions["reading_exercise"]
# choices = st.session_state.questions["choices"]

# Initialize score and asked questions tracker
if "score" not in st.session_state:
    st.session_state.score = 0
    
if "is_correct" not in st.session_state:
    st.session_state.is_correct = {idx: None for idx in range(len(questions["questions"]))}

if "answers" not in st.session_state:
    st.session_state.answers = {idx: None for idx in range(len(questions["questions"]))}

if "disabled" not in st.session_state:
    st.session_state.disabled = {idx: False for idx in range(len(questions["questions"]))}    

if "icons" not in st.session_state:
    st.session_state.icons = {}

if "test_complete" not in st.session_state:
    st.session_state.test_complete = False

if "answers_checked" not in st.session_state:
    st.session_state.answers_checked = {idx: False for idx in range(len(questions["questions"]))}
    

# Show the score on the sidebar
st.sidebar.title(f"Reading exercises \n 🔸 {current_mode}")
st.sidebar.write(
    f"Score: {st.session_state.score} correct out of {len(questions["questions"])}")

question_emojis = ["❓", "🔎", "🧠", "🏆", "📚", "🎯", "💡"]
choices_colors = [":violet", ":orange", ":blue"]

def ask_question(question_data, idx):
    with st.container(
        key=f"question-container-{idx}"):
        emoji = st.session_state.icons[idx]
        
        st.write(f"{emoji} {question_data['question']}")
                
        correct_answer = question_data["correct_answer"]

        col1, col2 = st.columns([12,1])
        # Display answer buttons
        selectbox_key = f"selectbox_{idx}"

        selectbox_disabled = st.session_state.disabled[idx]
        
        default_answer = st.session_state.answers[idx]
        
        with col1:
            selected_answer = st.segmented_control(
                options=question_data["choices"], 
                label="Select an option", 
                label_visibility="collapsed",
                disabled=selectbox_disabled,
                key=selectbox_key, 
                default=default_answer,
                selection_mode="single"
            )
            
            if selected_answer != st.session_state.answers[idx]:
                st.session_state.answers[idx] = selected_answer
                st.rerun()
        
        with col2:
            if st.session_state.answers[idx]:
                st.write(":rainbow[🖋]")

        if st.session_state.test_complete and not st.session_state.answers_checked[idx]:
            
            # Check if the selected option corresponds to the correct answer's letter
            is_correct_answer = correct_answer == selected_answer
            st.session_state.is_correct[idx] = is_correct_answer
            if is_correct_answer:
                st.session_state.score += 1

            # Disable further answers for this question
            st.session_state.disabled[idx] = True
            st.session_state.answers_checked[idx] = True
            st.rerun()

        # Display feedback message after answering
        if st.session_state.is_correct[idx] is not None:
            selected_option = st.session_state.answers[idx]
            question_answer = correct_answer

            if st.session_state.is_correct[idx] is True:
                st.success(f"Correct! You answered: :green[{selected_option}].")
            else:
                st.error(
                    f"Wrong! You selected :red[{selected_option}], \n but the correct answer is :green[{question_answer}]."
                )

col1, col2 = st.columns([1,1])
with col1:
    with st.container(
            key=f"question-container-text"
        ):
            st.header(questions["title"] if questions["title"] is not None else "")
            st.markdown(f'<div class="notepad"><div class="top"></div><div class="paper">{questions["text"]}</div></div><br/>', unsafe_allow_html=True)

shuffled_emojis = question_emojis.copy()
random.shuffle(shuffled_emojis)

# Display questions
with col2:
    for idx, question in enumerate(questions['questions']):
        if idx not in st.session_state.icons:
            emoji = shuffled_emojis[idx] if idx < len(shuffled_emojis) else random.choice(question_emojis)
            st.session_state.icons[idx] = emoji
        ask_question(question, idx)

st.divider()
# Display the final score
info_text = f"You have scored: {st.session_state.score} out of {len(questions['questions'])}"

col1, col2, col3 = st.columns([1, 2, 1])
# Check if all questions have been answered
if all(is_correct is not None for is_correct in st.session_state.is_correct.values()):
    # If all questions are correct, show balloons!
    log_reading_exercise(
        user_id=USER_ID, 
        title=questions["title"] if questions["title"] is not None else "", 
        level=available_modes[current_mode],
        text=questions["text"],
        score=st.session_state.score,
        total_questions=len(st.session_state.is_correct)
        )
    if all(is_correct is True for is_correct in st.session_state.is_correct.values()):
        st.balloons()
else:
    with col2:
        if st.button(
            key="reading-submit-button",
            label="Submit my answers!",
            disabled=st.session_state.test_complete,
            use_container_width=True
        ):
            st.session_state.test_complete = True
            st.rerun()
        if st.session_state.test_complete:
            st.info(info_text)

with col2:
    # Ask if the user wants a new set of questions
    if st.button("Get me some fresh questions!  🎲", use_container_width=True):
        refresh_test()
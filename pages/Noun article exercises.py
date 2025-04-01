import json
import random
import time
import streamlit as st
from database.db_helpers_exercises import log_noun_irregular_article_exercise, log_noun_regular_article_exercise
from question_generation import generate_noun_irregular_article_exercise, generate_noun_regular_article_exercise
from streamlit_helpers import set_background, load_css
from word_translation import translate_to_english

st.set_page_config(
    page_title="Noun Article Exercises - AI Language Trainer", 
    page_icon="📖",
    layout="wide")
set_background()
load_css()
st.title("Noun Article Exercises")
st.header("Practice choosing the correct German articles: *der, die, das*.")

available_modes = {
    "Irregular nouns": "noun_irregular_article_exercises", 
    "Regular nouns": "noun_regular_article_exercises"
}

mode_container = st.container(key="stButtonGroup-container-mode")
with mode_container:
    current_mode = st.segmented_control(
        label="Exercises with:", 
        label_visibility="collapsed", 
        options=list(available_modes.keys()), 
        default="Irregular nouns",
        )

st.divider()

def refresh_test():
    # Reset only necessary session state variables
    if "session_mode" in st.session_state:
        if st.session_state.session_mode == "noun_irregular_article_exercises":
            st.session_state.questions = generate_noun_irregular_article_exercise()
        elif st.session_state.session_mode == "noun_regular_article_exercises":
            st.session_state.questions = generate_noun_regular_article_exercise()
    questions = st.session_state.questions["questions"]
    st.session_state.score = 0
    st.session_state.answers = {idx: None for idx in range(len(questions))}
    st.session_state.disabled = {idx: None for idx in range(len(questions))}
    st.session_state.is_correct = {idx: None for idx in range(len(questions))}
    st.session_state.translation = {idx: None for idx in range(len(questions))}
    st.session_state.icons = {}
    
    # Re-run the script to update UI without full reload
    st.rerun()
    
USER_ID = 1  # Placeholder for session
    
if "session_mode" not in st.session_state or st.session_state.session_mode not in available_modes.values():
    st.session_state.session_mode = "noun_irregular_article_exercises"
    refresh_test()

if current_mode and available_modes[current_mode] != st.session_state.session_mode:
    st.session_state.session_mode = available_modes[current_mode]
    refresh_test()

if "questions" not in st.session_state:
    if st.session_state.session_mode == "noun_irregular_article_exercises":
        st.session_state.questions = generate_noun_irregular_article_exercise()
    elif st.session_state.session_mode == "noun_regular_article_exercises":
        st.session_state.questions = generate_noun_regular_article_exercise()
    st.session_state.llm_called = True
else:
    st.session_state.llm_called = False
questions = st.session_state.questions["questions"]

# Initialize score and asked questions tracker
if "score" not in st.session_state:
    st.session_state.score = 0
    
if "is_correct" not in st.session_state:
    st.session_state.is_correct = {idx: None for idx in range(len(questions))}

if "answers" not in st.session_state:
    st.session_state.answers = {idx: None for idx in range(len(questions))}

if "disabled" not in st.session_state:
    st.session_state.disabled = {idx: None for idx in range(len(questions))}

if "translation" not in st.session_state:
    st.session_state.translation = {idx: None for idx in range(len(questions))}

if "icons" not in st.session_state:
    st.session_state.icons = {}
    
seen_nouns = set()

# Show the score on the sidebar
st.sidebar.title("Noun article exercises")
st.sidebar.write(
    f"Score: {st.session_state.score} correct out of {len(questions)}")

question_emojis = ["❓", "🔎", "🧠", "🏆", "📚", "🎯", "💡"]
choices_colors = [":violet", ":orange", ":blue"]

def ask_question(question_data, idx):
    with st.container(
        key=f"question-container-{idx}"):
        emoji = st.session_state.icons[idx]
        
        col1, col2  = st.columns([7, 1])
        with col1:
            st.write(f"{emoji} {question_data['question']}")
        with col2:
            
            translation_disabled = False
            if st.session_state.translation[idx] is not None:
                translation_disabled = True
            if st.button(
                label=":material/Translate:", 
                key=f"translate-button-{idx}",
                disabled=translation_disabled
            ):
                translation = translate_to_english(question_data['noun'])
                if translation:
                    st.session_state.translation[idx] = translation
                    st.rerun()
        choices = question_data["choices"]
        correct_answer = question_data["correct_answer"]
        # Disable all buttons if an answer is selected
        if st.session_state.answers[idx]:
            st.session_state.disabled[idx] = True

        columns = st.columns(3)
        # Display answer buttons
        for i, option in enumerate(choices):
            button_key = f"question_{idx}_{i}"

            # If the question is disabled, disable all buttons
            disabled = st.session_state.disabled[idx] or correct_answer == st.session_state.answers[idx]

            button_text = f"{choices_colors[i]}[⟡] {option}"
            col = columns[i % 3]
            with col:
                if st.button(button_text, key=button_key, disabled=disabled, use_container_width=True):

                    # Update session state with selected answer
                    st.session_state.answers[idx] = option

                    # Check if the selected option corresponds to the correct answer's letter
                    is_correct_answer = correct_answer == option
                    st.session_state.is_correct[idx] = is_correct_answer
                    if is_correct_answer:
                        st.toast(body="Correct answer!", icon="✅")
                        time.sleep(0.3)
                        st.session_state.score += 1
                        # TODO: track_progress(question_id=question_data.get("id"), is_correct=True)

                    else:
                        st.toast(body="Wrong answer", icon="❗")
                        time.sleep(0.3)
                        # TODO: track_progress(question_id=question_data.get("id"), is_correct=False)

                    # Disable further answers for this question
                    st.session_state.disabled[idx] = True
                    
                    if st.session_state.session_mode == "noun_irregular_article_exercises":
                        log_noun_irregular_article_exercise(USER_ID, question_data["noun_id"], st.session_state.is_correct[idx])
                    elif st.session_state.session_mode == "noun_regular_article_exercises":
                        log_noun_regular_article_exercise(USER_ID, question_data["noun_id"], st.session_state.is_correct[idx])
                    log_noun_irregular_article_exercise(USER_ID, question_data["noun_id"], st.session_state.is_correct[idx])
                    st.rerun()
                    
        if st.session_state.translation[idx] is not None:
            st.info(f"Translation: {question_data['noun']} :material/line_end_arrow: {st.session_state.translation[idx]}")

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
                

columns = st.columns([1, 0.1, 1])
left_col, spacer, right_col = columns

shuffled_emojis = question_emojis.copy()
random.shuffle(shuffled_emojis)

# Display questions
for idx, question in enumerate(questions):
    if idx not in st.session_state.icons:
        emoji = shuffled_emojis[idx] if idx < len(shuffled_emojis) else random.choice(question_emojis)
        st.session_state.icons[idx] = emoji
    with left_col if idx % 2 == 0 else right_col:
        ask_question(question, idx)

st.divider()
# Display the final score
info_text = f"You have scored: {st.session_state.score} out of {len(questions)}"

col1, col2, col3 = st.columns([1, 2, 1])
# Check if all questions have been answered
if all(is_correct is not None for is_correct in st.session_state.is_correct.values()):
    info_text = f"{info_text} \n\n You've completed all the questions! 🎆"
    with col2:
        st.info(info_text)
    # If all questions are correct, show balloons!
    if all(is_correct is True for is_correct in st.session_state.is_correct.values()):
        st.balloons()
else:
    with col2:
        st.info(info_text)

with col2:
    # Ask if the user wants a new set of questions
    if st.button("Get me some fresh questions!  🎲", use_container_width=True):
        refresh_test()
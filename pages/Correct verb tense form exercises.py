import random
import time
import streamlit as st
from database.db_helpers_exercises import log_verb_exercise
from question_generation import generate_verb_exercise

st.set_page_config(
    page_title="Verb Tense Exercises - AI Language Trainer", 
    page_icon="📖",
    layout="wide")
st.title("Verb Tense Exercises")
st.write("Complete the following sentences with the verb in the given tense form.")

def refresh_test():
    # Reset only necessary session state variables
    st.session_state.questions = generate_verb_exercise()  # Get new questions
    questions = st.session_state.questions["questions"]
    st.session_state.score = 0
    st.session_state.answers = {idx: None for idx in range(len(questions))}
    st.session_state.disabled = {idx: None for idx in range(len(questions))}
    st.session_state.is_correct = {idx: None for idx in range(len(questions))}
    st.session_state.icons = {}
    
    # Re-run the script to update UI without full reload
    st.rerun()
    
USER_ID = 1  # Placeholder for session

if "questions" not in st.session_state:
    # Call the LLM once and store the result
    st.session_state.questions = generate_verb_exercise()
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

if "icons" not in st.session_state:
    st.session_state.icons = {}
    
seen_nouns = set()

# Show the score on the sidebar
st.sidebar.title("Noun article exercises")
st.sidebar.write(
    f"Score: {st.session_state.score} correct out of {len(questions)}")

question_emojis = ["❓", "🔎", "🧠", "🏆", "📚", "🎯", "💡"]

def ask_question(question_data, idx):
    form = st.form(f"verb_exercise_form_{idx}")
    emoji = st.session_state.icons[idx]
    form.write(f"{emoji} {question_data['question']}")
    correct_answer = question_data["correct_answer"]
    # Disable all buttons if an answer is selected
    if st.session_state.answers[idx]:
        st.session_state.disabled[idx] = True
        
    user_input_content = ""
    if st.session_state.answers[idx]:
        user_input_content = st.session_state.answers[idx]

            
    # If the question is disabled, disable all buttons
    disabled = st.session_state.disabled[idx] or correct_answer == st.session_state.answers[idx]
    
    # Text input for user to type the answer
    user_input = form.text_input(
        "Your answer:",
        value=user_input_content,
        key=f"text_{idx}",
        disabled=disabled,
        placeholder="Write your answer here."
    )
    
    form_submit_button = form.form_submit_button(label="Submit answer", disabled=disabled, use_container_width=True)
    
    if form_submit_button:

        # Update session state with selected answer
        st.session_state.answers[idx] = user_input.strip()

        # Check if the selected option corresponds to the correct answer's letter
        is_correct_answer = correct_answer == user_input.strip()
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
        
        # Log the response without querying the database
        log_verb_exercise(USER_ID, question_data["verb_id"], st.session_state.is_correct[idx])
        st.rerun()

    # Display feedback message after answering
    if st.session_state.is_correct[idx] is not None:
        selected_option = st.session_state.answers[idx]
        question_answer = correct_answer

        if st.session_state.is_correct[idx] is True:
            form.success(f"Correct! You answered: {selected_option}.")
        else:
            form.error(
                f"Wrong! You selected {selected_option}, \n but the correct answer is {question_answer}."
            )
                
    st.markdown("<br><br>", unsafe_allow_html=True)


columns = st.columns([1, 0.2, 1])
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
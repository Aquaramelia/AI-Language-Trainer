import streamlit as st
from database.db_helpers_exercises import log_noun_exercise
from question_generation import generate_noun_exercise
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(
    page_title="Noun Article Exercises - AI Language Trainer", page_icon="📖")

USER_ID = 1  # Placeholder for session

if "exercise_data" not in st.session_state:
    # Call the LLM once and store the result
    st.session_state.exercise_data = generate_noun_exercise()
    st.session_state.llm_called = True
else:
    st.session_state.llm_called = False

# Initialize score and asked questions tracker
if "score" not in st.session_state:
    st.session_state.score = 0

if "asked_questions" not in st.session_state:
    st.session_state["asked_questions"] = []

st.title("German Article Trainer 🇩🇪")
st.write("Practice choosing the correct German articles: *der, die, das*.")

exercise_data = st.session_state.exercise_data

# Sidebar to show score
st.sidebar.title("Noun article exercises")
st.sidebar.write(
    f"Score: {st.session_state.score} correct out of {len(exercise_data['questions'])}")

if "message" in exercise_data:
    st.info(exercise_data["message"])
else:
    for i, q in enumerate(exercise_data["questions"]):
        if q["noun_id"] in st.session_state["asked_questions"]:
            continue  # Skip if the question has already been asked

        st.subheader(q["question"])

        # Initialize session state for each question if not set
        if f"selected_{q['noun_id']}" not in st.session_state:
            st.session_state[f"selected_{q['noun_id']}"] = None
        if f"submitted_{q['noun_id']}" not in st.session_state:
            st.session_state[f"submitted_{q['noun_id']}"] = False
        if f"answered_{q['noun_id']}" not in st.session_state:
            # Flag to track if answered
            st.session_state[f"answered_{q['noun_id']}"] = False

        # Disable the radio button and submit button if the question is already answered
        is_answered = st.session_state[f"answered_{q['noun_id']}"]

        # Radio button stores selection in session state
        selected = st.radio(
            "Select the correct article:",
            q["options"],
            index=q["options"].index(
                st.session_state[f"selected_{q['noun_id']}"])
            if st.session_state[f"selected_{q['noun_id']}"] in q["options"]
            else 0,
            key=f"radio_{q['noun_id']}_{i}",
            disabled=is_answered  # Disable if already answered
        )

        # Button triggers submission and hides after answer
        submit_button = st.button(
            f"Submit {q['question']}",
            key=f"button_{q['noun_id']}_{i}",
            disabled=is_answered  # Disable button after submission
        )

        # Only increment the score if the user hasn't already answered the question
        if submit_button:
            is_correct = selected == q["answer"]
            if is_correct:
                st.success("✅ Correct!")
                # Increment score for correct answer
                st.session_state.score += 1
            else:
                st.error(
                    f"❌ Incorrect! The correct answer is **{q['answer']}**.")

            # Mark the question as answered so the score won't be added again
            st.session_state[f"answered_{q['noun_id']}"] = True
            st.session_state["asked_questions"].append(
                q["noun_id"])  # Track this question as asked

            # Log the response without querying the database
            log_noun_exercise(USER_ID, q["noun_id"], is_correct)

            # Force a re-run to reflect the updated score immediately
            st.rerun()

        # Ensure the selected answer gets locked after submission by updating session state
        if is_answered:
            st.session_state[f"selected_{q['noun_id']}"] = selected

# Check if all questions have been answered
if len(st.session_state["asked_questions"]) == len(exercise_data["questions"]):
    # Show popup message when all questions are answered
    st.info("🎉 Congratulations! You've completed all the questions!")

    # Ask if the user wants to reload and get a fresh set of questions
    reload_button = st.button("Reload Page for New Set of Questions")

    if reload_button:
        # Trigger a full page reload (not just rerun)
        streamlit_js_eval(js_expressions="parent.window.location.reload()")

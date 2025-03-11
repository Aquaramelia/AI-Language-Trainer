import streamlit as st
from database.db_helpers_exercises import log_verb_exercise
from question_generation import generate_verb_exercise

st.set_page_config(page_title="Verb Exercises - AI Language Trainer", page_icon="📖")

USER_ID = 1  # Placeholder for session

if "exercise_data" not in st.session_state:
    # Call the LLM once and store the result
    st.session_state.exercise_data = generate_verb_exercise()
    st.session_state.llm_called = True
else:
    st.session_state.llm_called = False

st.title("German Verb Trainer 🇩🇪")
st.write("Practice typing the correct tense form of the verbs.")

exercise_data = st.session_state.exercise_data

if "message" in exercise_data:
    st.info(exercise_data["message"])
else:
    for i, q in enumerate(exercise_data["questions"]):
        st.subheader(q["question"])

        # Initialize session state for each question if not set
        if f"answer_{q['verb_id']}" not in st.session_state:
            st.session_state[f"answer_{q['verb_id']}"] = ""

        if f"submitted_{q['verb_id']}" not in st.session_state:
            st.session_state[f"submitted_{q['verb_id']}"] = False

        # Text input for user to type the answer
        user_input = st.text_input(
            "Your answer:",
            value=st.session_state[f"answer_{q['verb_id']}"],
            key=f"text_{q['verb_id']}"
        )

        # Button to submit answer
        if st.button(f"Submit {q['question']}", key=f"button_{q['verb_id']}"):
            st.session_state[f"submitted_{q['verb_id']}"] = True
            # Store cleaned input
            st.session_state[f"answer_{q['verb_id']}"] = user_input.strip()

        # Show result if submitted
        if st.session_state[f"submitted_{q['verb_id']}"]:
            is_correct = st.session_state[f"answer_{q['verb_id']}"] == q["answer"]
            if is_correct:
                st.success("✅ Correct!")
            else:
                st.error(
                    f"❌ Incorrect! The correct answer is **{q['answer']}**.")

            # Log response without querying the database
            log_verb_exercise(USER_ID, q["verb_id"], is_correct)

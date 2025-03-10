import streamlit as st
from database.db_helpers_exercises import log_noun_exercise
from question_generation import generate_noun_exercise

USER_ID = 1  # Placeholder for session

if "exercise_data" not in st.session_state:
    st.session_state.exercise_data = generate_noun_exercise()  # Call the LLM once and store the result
    st.session_state.llm_called = True
else:
    st.session_state.llm_called = False

st.title("German Article Trainer 🇩🇪")
st.write("Practice choosing the correct German articles: *der, die, das*.")

exercise_data = st.session_state.exercise_data

if "message" in exercise_data:
    st.info(exercise_data["message"])
else:
    for i, q in enumerate(exercise_data["questions"]):
        st.subheader(q["question"])

        # Initialize session state for each question if not set
        if f"selected_{q['noun_id']}" not in st.session_state:
            st.session_state[f"selected_{q['noun_id']}"] = None
        if f"submitted_{q['noun_id']}" not in st.session_state:
            st.session_state[f"submitted_{q['noun_id']}"] = False

        # Radio button stores selection in session state
        st.session_state[f"selected_{q['noun_id']}"] = st.radio(
            "Select the correct article:", q["options"], 
            index=q["options"].index(st.session_state[f"selected_{q['noun_id']}"])
            if st.session_state[f"selected_{q['noun_id']}"] in q["options"]
            else 0, 
            key=f"radio_{q['noun_id']}"
        )

        # Button triggers submission
        if st.button(f"Submit {q['question']}", key=f"button_{q['noun_id']}"):
            st.session_state[f"submitted_{q['noun_id']}"] = True

        # Show result if submitted
        if st.session_state[f"submitted_{q['noun_id']}"]:
            is_correct = st.session_state[f"selected_{q['noun_id']}"] == q["answer"]
            if is_correct:
                st.success(
                    "✅ Correct!"
                )
            else:
                st.error(
                    f"❌ Incorrect! The correct answer is **{q['answer']}**."
                )

            # Log response without querying the database
            log_noun_exercise(USER_ID, q["noun_id"], is_correct)

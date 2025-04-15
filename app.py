import streamlit as st
from st_helpers.general_helpers import set_background, load_css


if "page_initialized" not in st.session_state or st.session_state.page_initialized == False:
    st.set_page_config(page_title="AI Language Trainer", layout="wide", page_icon="📖")
    set_background()
    load_css()
    st.session_state.page_initialized = True
    

if "login_successful" not in st.session_state:
    st.session_state.login_successful = False

def login_screen():
    st.title("Welcome to the AI Language Trainer!")
    st.subheader("Please log in to access the application.")
    # Minimal stub nav just to satisfy Streamlit requirement (even when logged out)
    current_page = st.navigation(pages=[st.Page(page="./app.py")], position="hidden")
    st.button("Log in with Google", on_click=st.login, key="login-button")
    return current_page

if not st.experimental_user.is_logged_in:
    current_page = login_screen()

else:
    if not st.session_state.login_successful:
        st.toast("You are logged in! Your progress will now be tracked.", icon="🎆")
        st.session_state.login_successful = True

    # Register your pages here    
    current_page = st.navigation(
        pages={
            "Exercises": [
                st.Page(page="./pages/noun_article_exercises.py", title="Noun article exercises", icon="🔤"),
                st.Page(page="./pages/vocabulary_exercises.py", title="Vocabulary exercises", icon="📕"),
                st.Page(page="./pages/verb_tense_exercises.py", title="Verb tense form exercises", icon="🖍"),
                st.Page(page="./pages/reading_exercises.py", title="Reading exercises", icon="📚"),
                st.Page(page="./pages/writing_exercises.py", title="Writing exercises", icon="📜")
            ],
            "Indexes & Glossaries": [
                st.Page(page="./pages/essay_index.py", title="Essay index", icon="📋"),
                st.Page(page="./pages/explore_vocabulary.py", title="Explore vocabulary", icon="🌍")
            ],
            "Statistics": [
                st.Page(page="./pages/dashboard.py", title="Dashboard", icon="📊", default=True)
            ]
        }
    )
    st.sidebar.button("Log out", on_click=st.logout)

    if current_page:
        current_page.run()
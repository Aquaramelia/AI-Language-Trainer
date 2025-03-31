import streamlit as st
from streamlit_helpers import load_css, set_background

st.set_page_config(page_title="Home - AI Language Trainer", page_icon="📖", layout="wide")
set_background()
load_css()
st.title("Welcome to the AI Language Trainer!")

if "session_mode" not in st.session_state or st.session_state.session_mode != "home":
    st.session_state.session_mode = "home"

st.sidebar.success("Select a page above to start training! 👆")
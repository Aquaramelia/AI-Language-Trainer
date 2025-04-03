import streamlit as st
from st_helpers.general_helpers import load_css, set_background
import st_helpers.progress_noun_articles as progress_noun_articles
import st_helpers.progress_heatmap as progress_heatmap
import st_helpers.progress_verb_tenses as progress_verb_tenses

st.set_page_config(page_title="Home - AI Language Trainer", page_icon="📖", layout="wide")
set_background()
load_css()
st.title("Welcome to the AI Language Trainer!")
st.divider()
if "session_mode" not in st.session_state or st.session_state.session_mode != "home":
    st.session_state.session_mode = "home"

st.sidebar.success("Select a page above to start training! 👆")



col1, col2 = st.columns([1,1])

# Show noun article statistics
with col1:
    
    with st.container(
        key="question-chart-articles"
    ):
        progress_noun_articles.return_chart()
with col2:
    with st.container(
        key="question-chart-verb-tenses"
    ):
        progress_verb_tenses.return_chart()

progress_heatmap.return_chart()
import streamlit as st
from database.db_helpers_exercises import get_practice_data
from st_helpers.general_helpers import load_css, set_background
import st_helpers.progress_noun_articles as progress_noun_articles
import st_helpers.progress_heatmap as progress_heatmap
import st_helpers.progress_verb_tenses as progress_verb_tenses
import st_helpers.progress_chart as progress_chart

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

practice_data = get_practice_data(user_id=1)

if practice_data.empty:
    st.write("No data available to generate progress charts.")
else:
    col1, col2 = st.columns([1,1])
    with col1:
        with st.container(key="chart-parent-container-1"):
            with st.container(key="chart-child-container-1"):
                progress_chart.return_chart(practice_data, 7, title="Your weekly progress")
    with col2:
        with st.container(key="chart-parent-container-2"):
            with st.container(key="chart-child-container-2"):
                progress_chart.return_chart(practice_data, 30, title="Your monthly progress")
            
    with st.container(key="heatmap-parent-container-1"):
        with st.container():
            progress_heatmap.return_chart(practice_data)
import streamlit as st
from database.db_helpers_exercises import get_essay_index, get_essay_content
from st_helpers.general_helpers import set_background, load_css

st.set_page_config(
    page_title="Essay Index - AI Language Trainer", 
    page_icon="📖",
    layout="wide")
set_background()
load_css()
st.title("Essay Index")
st.header("Take a moment to review your past writing exercises!")
st.divider()
USER_ID = 1

col1, col2 = st.columns([1, 3])
with col1:
    essay_titles = get_essay_index(user_id=USER_ID)
    st.markdown("""
        <style>
        [data-testid="stSelectboxVirtualDropdown"] * {
        font-size: 99% !important;
        }
        </style>
    """, unsafe_allow_html=True)
    with st.container(
        key="selectbox-essay-index-container"
    ):
        title_selection = st.selectbox(
            key="title-selectbox",
            options=[f"{t["level"]} - {t["title"]}" for t in essay_titles],
            label="Select a writing exercise:"
        )
with col2:
    if title_selection:
        level, title = title_selection.split(" - ", 1)
        essays = get_essay_content(user_id=USER_ID, title=title)
        if essays:
            with st.container(
                key="essay-index-title"
            ):
                colA, colB = st.columns([1,10])
                with colB:
                    st.header(title_selection)
                with colA:
                    level = essays["level"]
                    if "A" in level:
                        color = "green"
                    elif "B" in level:
                        color = "blue"
                    elif "C" in level:
                        color = "violet"
                    else:
                        color = "orange"
                    st.badge(label=level, color=color)
            st.markdown(f'<div class="notepad"><div class="top"></div><div class="paper">{essays["prompt"]}</div></div><br/>', unsafe_allow_html=True)
            with st.container(
                key="essay-index-content"
            ):
                colA, colB, colC = st.columns([1,5,1])
                with colB:
                    st.write(essays["answer"] if essays["answer"] is not None else "")
            with st.container(
                    key=f"response-container-"
                ):
                    with st.chat_message(
                        name="ai",
                        avatar="🐤"):
                        st.write(essays["correction"] if essays["correction"] is not None else "")
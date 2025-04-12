import streamlit as st
from database.db_helpers_dictionary import get_category_all, get_categories
from st_helpers.general_helpers import set_background, load_css
import pandas as pd
from st_helpers.general_helpers import safe_join

st.set_page_config(
    page_title="Explore Vocabulary - AI Language Trainer",
    page_icon="📖",
    layout="wide")
set_background()
load_css()
st.title("Explore Vocabulary")
st.header("Discover new words across thematical categories\n Build your own vocabulary inventory!")
st.divider()
USER_ID = 1

categories = get_categories()

st.markdown("""
    <style>
    [data-testid="stSelectboxVirtualDropdown"] * {
    font-size: 99% !important;
    }
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])
category_selection = ""
with col1:
    with st.container(
        key="selectbox-essay-index-container"
    ):
        category_selection = st.selectbox(
            key="title-selectbox",
            options=[c for c in categories],
            label="Select a category to view:",
            index=None
        )
        if category_selection:
            data = get_category_all(category_selection)
            category_df = pd.DataFrame(data)
            category_df = category_df[["word", "senses"]].copy()
            category_df["senses_joined"] = category_df["senses"].apply(safe_join)
            
            category_df["word_md"] = category_df.apply(
                lambda row: f"**Word**: {row['word']}  \n**Senses**: {row['senses_joined']}", axis=1
            )

            st.dataframe(
                data=category_df["word_md"],
                use_container_width=True,
                selection_mode="multi-row",
                hide_index=True,
                column_config={
                    "word_md": "Words in category",
                    "_index": ""
                }
            )

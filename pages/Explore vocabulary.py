import re
import streamlit as st
from database.db_helpers_dictionary import get_category_all, get_categories
from st_helpers.general_helpers import set_background, load_css
import pandas as pd
from st_helpers.general_helpers import safe_join
from st_helpers.aggrid_explore_vocabulary import display_grid

st.set_page_config(
    page_title="Explore Vocabulary - AI Language Trainer",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed")
set_background()
load_css()
st.title("Explore Vocabulary")
st.header("Discover new words across thematical categories - build your own vocabulary inventory!")
st.divider()
USER_ID = 1

if "last_word_displayed" not in st.session_state:
    st.session_state.last_word_displayed = ""
if "last_category" not in st.session_state:
    st.session_state.last_category = ""
if "last_category_dataframe" not in st.session_state:
    st.session_state.last_category_dataframe = None

categories = get_categories()

st.markdown("""
    <style>
    [data-testid="stSelectboxVirtualDropdown"] * {
    font-size: 99% !important;
    }
    </style>
""", unsafe_allow_html=True)

with st.container(
    key="question-container-"
):
    col1, col2 = st.columns([1, 2])
    category_selection = ""
    matching_row = None
    category_df = st.session_state.last_category_dataframe
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
            if category_selection and category_selection != st.session_state.last_category:
                data = get_category_all(category_selection)
                st.code(f"🔍 Loaded {len(data)} entries from category: {category_selection}")
                st.toast("Retrieving category data...", icon="⏳")
                category_df = pd.DataFrame(data)
                category_df["senses_joined"] = category_df["senses"].apply(safe_join)
                
                category_df["word_md"] = category_df.apply(
                    lambda row: f"<b>{row['word']} </b><i style='color: #96c1ee;'>{row['senses_joined']}</i>", axis=1
                )
                st.session_state.last_category = category_selection
                st.session_state.last_category_dataframe = category_df
                
            if category_df is not None:
                grid_response = display_grid(category_df=category_df, category_selection=category_selection)

                # Get selected row
                selected = grid_response['selected_rows']
                selected_word = ""
                if selected is not None:
                    selected_word_md = selected.iloc[0]["word_md"]  # Extract the selected word_md
                    print(selected_word_md)
                    if selected_word_md is not None:
                        # Use regex to extract the word between <b> and </b> tags
                        match = re.search(r'<b>(.*?)</b>', selected_word_md)
                        if match:
                            selected_word = match.group(1).strip()  # This will give you the word "Kohlenhydrathaushalt"
                            st.session_state.last_word_displayed = selected_word
                else:
                    selected_word = st.session_state.last_word_displayed
                if selected_word: 
                    matching_rows = category_df[category_df["word"] == selected_word]     
                    if not matching_rows.empty:
                        matching_row = matching_rows.iloc[0]
        
        with col2:
            if matching_row is not None:
                st.write("Word: ", matching_row.get("word"))
                st.write("Forms: ", matching_row.get("forms"))
                st.write("Senses: ", matching_row.get("senses"))
                st.write("Glosses: ", matching_row.get("glosses"))
                st.write("Examples: ", matching_row.get("examples"))
                st.write("Derived: ", matching_row.get("derived"))
                st.write("Related: ", matching_row.get("related"))
                st.write("Antonyms: ", matching_row.get("antonyms"))
                st.write("Synonyms: ", matching_row.get("synonyms"))
                st.write("Hyponyms: ", matching_row.get("hyponyms"))
                
import re
import streamlit as st
from database.db_helpers_dictionary import get_category_all, get_categories
from st_helpers.general_helpers import set_background, load_css
import pandas as pd
from st_helpers.general_helpers import safe_join, safe_bullets, safe_table_cell
from st_helpers.aggrid_explore_vocabulary import display_grid
from annotated_text import annotated_text, annotation, parameters

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
                st.code(f"🔍 Loaded {len(data)} entries in {category_selection}")
                st.toast("Retrieving category data...", icon="⏳")
                category_df = pd.DataFrame(data)
                category_df["senses_joined"] = category_df["senses"].apply(safe_join, limit=30)
                
                category_df["word_md"] = category_df.apply(
                    lambda row: f'<b style="font-size: 120% !important;">{row["word"]} </b><i style="color: #96c1ee;">{row["senses_joined"]}</i>', axis=1
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
                        match = re.search(r'<b style="font-size: 120% !important;">(.*?)</b>', selected_word_md)
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
                st.markdown("<br/>", unsafe_allow_html=True)
                with st.container(
                    key="explore-vocabulary-card"
                ):
                    with st.container(
                        key="explore-vocabulary-title"
                    ):
                        word = matching_row.get("word")
                        if word:
                            parameters.PADDING = "0.5em 0.75rem"
                            annotated_text(
                                annotation(
                                    word,
                                    "",
                                    background="rgb(8,0,99)",
                                    color="rgb(255,185,77)",
                                    font_family="Delius",
                                    border="1px solid #ffffffa8",
                                    font_size="150%",
                                    text_align="center"
                                )
                            )
                    with st.container(
                        key="explore-vocabulary-glosses"
                    ):
                        glosses = matching_row.get("glosses")
                        if glosses and glosses != "[]":
                            st.write(safe_join(glosses))
                    st.divider()    
                    
                            
                    colA, colB = st.columns([1,1])
                    with colA:
                        forms = matching_row.get("forms")
                        if forms and forms != "[]":
                            with st.expander(
                                label="Available word forms: ",
                                icon="📌"
                            ):
                                st.write(safe_join(forms))
                    with colB:
                        senses = matching_row.get("senses")
                        if senses and senses != "[]":
                            with st.expander(
                                label="In topics: ",
                                icon="📑"
                            ):
                                st.write(safe_join(senses))                                            
                    colA, colB = st.columns([1,1])
                    with colA:
                        with st.container(
                            key="explore-vocabulary-derived"
                        ):
                            derived = matching_row.get("derived")
                            if derived and derived != "[]":
                                with st.expander(
                                    label=" Derived words: ",
                                    icon="🧶"
                                ):
                                    st.write(safe_join(derived))
                    with colB:
                        with st.container(
                            key="explore-vocabulary-related"
                        ):
                            related = matching_row.get("related")
                            if related and related != "[]":
                                with st.expander(
                                    label=" Related words: ",
                                    icon="🌳"
                                ):
                                    st.write(safe_join(related))
                    with colA:
                        with st.container(
                            key="explore-vocabulary-antonyms"
                        ):
                            antonyms = matching_row.get("antonyms")
                            if antonyms and antonyms != "[]":
                                with st.expander(
                                    label=" Antonyms: ",
                                    icon="↔️"
                                ):
                                    st.write(safe_join(antonyms))
                    with colB:
                        with st.container(
                            key="explore-vocabulary-synonyms"
                        ):
                            synonyms = matching_row.get("synonyms")
                            if synonyms and synonyms != "[]":
                                with st.expander(
                                    label=" Synonyms: ",
                                    icon="🔁"
                                ):
                                    st.write(safe_join(synonyms))
                    with colA:
                        with st.container(
                            key="explore-vocabulary-hyponyms"
                        ):
                            hyponyms = matching_row.get("hyponyms")
                            if hyponyms and hyponyms != "[]":
                                with st.expander(
                                    label=" Hyponyms: ",
                                    icon="🐾"
                                ):
                                    st.write(safe_join(hyponyms))
                    with colB:
                        with st.container(
                            key="explore-vocabulary-hypernyms"
                        ):
                            hypernyms = matching_row.get("hypernyms")
                            if hypernyms and hypernyms != "[]":
                                with st.expander(
                                    label=" Hypernyms: ",
                                    icon="🌍"
                                ):
                                    st.write(safe_join(hypernyms))                
                    with st.container(
                        key="explore-vocabulary-examples"
                    ):
                        examples = matching_row.get("examples")
                        if examples and examples != "[]":
                            st.info(safe_join(value=examples, delimiter="<br>"))
import re
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode, StAggridTheme
from st_helpers.aggrid_html_cell_renderer import HtmlCellRenderer
import streamlit as st
from database.db_helpers_dictionary import get_category_all, get_categories
from st_helpers.general_helpers import set_background, load_css
import pandas as pd
from st_helpers.general_helpers import safe_join

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
    st.session_state.last_category_dataframe = pd.DataFrame()

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
    col1, col2 = st.columns([1, 1])
    category_selection = ""
    matching_row = ""
    category_df = None
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
                st.toast("Retrieving category data...")
                category_df = pd.DataFrame(data)
                category_df = category_df[["word", "senses", "forms", "glosses", "examples"]].copy()
                category_df["senses_joined"] = category_df["senses"].apply(safe_join)
                
                category_df["word_md"] = category_df.apply(
                    lambda row: f"<b>{row['word']} </b><i style='color: #96c1ee;'>{row['senses_joined']}</i>", axis=1
                )
                st.session_state.last_category = category_selection
                st.session_state.last_category_dataframe = category_df
            else:
                category_df = st.session_state.last_category_dataframe
                
            CustomHtmlCellRenderer = JsCode(HtmlCellRenderer)
            
            custom_theme = StAggridTheme(base="quartz").withParams(
                fontSize=16,
                rowBorder=False,
                backgroundColor="#273aa4c7",
                foregroundColor="#fff"
            ).withParts('iconSetAlpine')  

            gb = GridOptionsBuilder.from_dataframe(category_df[["word_md"]])
            gb.configure_column(
                "word_md",
                header_name=f"Words in category: {category_selection}",
                # cellRenderer="function(params) { return params.value; }",
                cellRenderer=CustomHtmlCellRenderer
            )

            gb.configure_selection(
                selection_mode="single",
                suppressRowDeselection=True,
                suppressRowClickSelection=False,
                pre_selected_rows=[0]
            )

            grid_options = gb.build()
            grid_options["masterDetail"] = False

            # Display grid
            grid_response = AgGrid(
                category_df[["word_md"]],
                gridOptions=grid_options,
                height=600,
                width='100%',
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                allow_unsafe_jscode=True,
                enable_enterprise_modules=False,
                fit_columns_on_grid_load=True,
                theme=custom_theme
            )

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
                # Now find the corresponding row in the original data DataFrame using the word
                matching_row = category_df[category_df["word"] == selected_word].iloc[0]
        
        with col2:
            if matching_row is not None:
                st.write("Word: ", matching_row.get("word"))
                st.write("Forms: ", matching_row.get("forms"))
                st.write("Senses: ", matching_row.get("senses"))
                st.write("Glosses: ", matching_row.get("glosses"))
                st.write("Examples: ", matching_row.get("examples"))
                
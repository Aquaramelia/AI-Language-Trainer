import streamlit as st
from database.db_helpers_exercises import get_practice_data
from st_helpers.general_helpers import load_css, set_background
import st_helpers.progress_noun_articles as progress_noun_articles
import st_helpers.progress_heatmap as progress_heatmap
import st_helpers.progress_verb_tenses as progress_verb_tenses
import st_helpers.progress_chart as progress_chart
import st_helpers.progress_vocabulary as progress_vocabulary
from st_helpers.vocabulary_helpers import available_modes,available_modes_r, return_chart_levels

set_background()
load_css()
    
st.title("Progress Dashboard")
st.header("This is your dashboard! Take a moment to explore and check out your results ✨")
st.divider()
if "session_mode" not in st.session_state or st.session_state.session_mode != "home":
    st.session_state.session_mode = "home"


st.sidebar.success("Select a page above to start training! 👆")

col1, col2 = st.columns([1,1])

# Show noun article exercise statistics
with col1:
    with st.container(
        key="question-chart-articles"
    ):
        progress_noun_articles.return_chart()
# Show verb tense exercise statistics
with col2:
    with st.container(
        key="question-chart-verb-tenses"
    ):
        progress_verb_tenses.return_chart()
    
    
# Show vocabulary learning statistics
practiced_levels = return_chart_levels()
col1, col2, col3, col4 = st.columns([1,1,1,1])
with col1:
    with st.container(
        key="question-chart-vocabulary-1"
    ):
        print(practiced_levels)
        print(available_modes_r)
        progress_vocabulary.return_chart(
            level=practiced_levels[0], 
            levelTitle=available_modes_r[practiced_levels[0]], 
            graphTitle="Vocabulary Card 1",
            colormap="purples",
            caption="This is your highest practiced level, well done!")
with col2:
    with st.container(
        key="question-chart-vocabulary-2"
    ):
        progress_vocabulary.return_chart(
            level=practiced_levels[1], 
            levelTitle=available_modes_r[practiced_levels[1]], 
            graphTitle="Vocabulary Card 2",
            colormap="pubu",
            caption="You're getting the hang of this level — great progress!")
with col3:
    with st.container(
        key="question-chart-vocabulary-3"
    ):
        progress_vocabulary.return_chart(
            level=practiced_levels[2], 
            levelTitle=available_modes_r[practiced_levels[2]], 
            graphTitle="Vocabulary Card 3",
            colormap="blues",
            caption="You're on your way! Keep going and watch your skills grow.")
with col4:
    with st.container(
        key="question-chart-vocabulary-4"
    ):
        selected_level = ""
        st.markdown('<style>[data-testid="stSelectboxVirtualDropdown"] * {font-size: 100% !important;}</style>', unsafe_allow_html=True)    
        level = st.selectbox(
            key="selectbox-vocabulary-level",
            options=available_modes.keys(),
            label="Select a vocabulary level:",
            label_visibility="visible"
        )
        progress_vocabulary.return_chart(
            level=available_modes[level] if level is not None else practiced_levels[3], 
            levelTitle=level if level is not None else available_modes[practiced_levels[3]],
            graphTitle="Vocabulary Card 4",
            colormap="bugn",
            caption="")
        

# Show weekly and monthly user progress statistics
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
            
    # Show yearly user progress statistics
    with st.container(key="heatmap-parent-container-1"):
        with st.container():
            progress_heatmap.return_chart(practice_data)
from numpy import select
import streamlit as st
from streamlit.runtime.state import session_state
from st_helpers.news_digest_helpers import return_article, execute_rss_ingestion, return_selectbox_feed_categories, update_article, display_url
from st_helpers.general_helpers import set_background, load_css
from st_helpers.aggrid_news_digest import display_grid
import pandas as pd
from annotated_text import annotated_text, annotation

st.set_page_config(
    page_title="News Digest - AI Language Trainer",
    page_icon="📖",
    layout="wide")
set_background()
load_css()

st.markdown("""
    <style>
    [data-testid="stSelectboxVirtualDropdown"] * {
    font-size: 99% !important;
    }
""", unsafe_allow_html=True)

st.title("News Digest")
st.header("Take a look at recent news from real German news feeds and choose some interesting ones!")
with st.container(
    key="news-digest-subtitle-caption"
):
    st.caption("Articles for practice may differ slighlty from the original ones.")
USER_ID = 1

if "last_feed" not in st.session_state:
    st.session_state.last_feed = ""
if "last_article_displayed" not in st.session_state:
    st.session_state.last_article_displayed = ""
if "last_feed_dataframe" not in st.session_state:
    st.session_state.last_feed_dataframe = ""
if "news_articles" not in st.session_state:
    st.toast("Loading content...", icon="⏳")
    st.session_state.news_articles = execute_rss_ingestion()

# State of generating new articles
if "feed_retrieval_in_progress" not in st.session_state:
    st.session_state.feed_retrieval_in_progress = False

col1, col2, col3 = st.columns([1, 2, 1])
generation_button_key = "generate-articles-button"

with col2:
    if st.button("Generate new articles! 🗞️", key=generation_button_key, disabled=st.session_state.feed_retrieval_in_progress, use_container_width=True):
        st.toast("Loading content...", icon="⏳")
        st.session_state.feed_retrieval_in_progress = True
        st.session_state.news_articles = execute_rss_ingestion()
        st.session_state.feed_retrieval_in_progress = False
        # Reset the button state before rerun
        del st.session_state[generation_button_key]
        st.rerun()
    
st.divider()

# Create tabs for different modes
tab_feed, tab_practice, tab_progress = st.tabs(["Browse feed", "Practice exercises", "My progress"])

# Feed tab

with tab_feed:
    with st.container(
        key="question-container-"
    ):
        col1, col2 = st.columns([1,2])
        feed_selection:str = ""
        matching_row = None
        feed_df = st.session_state.last_feed_dataframe
        with col1:
            with st.container(
                key="selectbox-news-browse-container"
            ):
                selectbox_selection = st.selectbox(
                    key="news-browse-selectbox",
                    options=return_selectbox_feed_categories(),
                    label="Select a feed to view news:",
                    index=None
                )
                if selectbox_selection:
                    feed_selection = selectbox_selection

                if feed_selection and feed_selection != st.session_state.last_feed:
                    articles_dict = [return_article(feed_selection, articles) for articles in st.session_state.news_articles[feed_selection]]
                    st.code(f"🔍 Loaded {len(st.session_state.news_articles[feed_selection])} entries from the RSS feed of {feed_selection}", wrap_lines=True)
                    st.toast("Displaying category...", icon="📒")
                    feed_df = pd.DataFrame(articles_dict)

                    st.session_state.last_feed = feed_selection
                    st.session_state.last_feed_dataframe = feed_df

                if feed_df is not None and type(feed_df) == pd.DataFrame:
                    grid_response = display_grid(feed_df=feed_df, feed_selection=feed_selection)

                    # Get selected row
                    selected = grid_response.selected_rows
                    selected_word = ""
                    if selected is not [] and selected is not None:
                        selected_article = selected.iloc[0]["title"]
                        if selected_article is not None:
                            st.session_state.last_article_displayed = selected_article
                    else:
                        selected_article = st.session_state.last_article_displayed
                    if selected_article:
                        matching_rows = feed_df[feed_df["title"] == selected_article]
                        if not matching_rows.empty:
                            matching_row = matching_rows.iloc[0]
                    elif st.session_state.last_feed is not None:
                        matching_rows = feed_df[feed_df["feed_name"] == st.session_state.last_feed]
                        if not matching_rows.empty:
                            first_row = matching_rows.iloc[0]
                        else:
                            first_row = None

        with col2:
            if matching_row is not None:
                with st.container(
                    key="news-digest-article-card"
                ):
                    col_title_1, col_title_2 = st.columns([4,1])
                    with col_title_1:
                        with st.container(
                            key="news-digest-article-title"
                        ):
                            title = matching_row.get("title", "")
                            annotated_text(
                                annotation(
                                    title,
                                    "",
                                    background="rgb(8,0,99)",
                                    color="rgb(255,185,77)",
                                    font_family="Delius",
                                    border="1px solid #ffffffa8",
                                    font_size="100%",
                                    text_align="center"
                                )
                            )
                        with st.container(
                            key="news-digest-article-url"
                        ):
                            url = matching_row.get("url", "")
                            display_url(url)
                        with st.container(
                            key="news-digest-article-published"
                        ):
                            feed_name = matching_row.get("feed_name", "")
                            published = matching_row.get("published", "")
                            st.write(feed_name + " - " + published)
                    with col_title_2:
                        if st.button(
                            label="Accept article & practice",
                            key="accept-article",
                            icon="✅",
                            use_container_width=True
                        ):
                            update_article(
                                url=matching_row.get("url"),
                                accepted=True
                            )
                            # Force-reload article data
                            st.session_state.last_feed_dataframe = None
                            st.rerun()
                        if st.button(
                            label="Reject article & continue",
                            key="reject-article",
                            icon="❌",
                            use_container_width=True
                        ):
                            update_article(
                                url=matching_row.get("url"),
                                accepted=False
                            )
                            # Force-reload article data
                            st.session_state.last_feed_dataframe = None
                            st.rerun()
                    st.divider()
                    with st.container(
                        key="news-digest-article-text"
                    ):
                        text = matching_row.get("text", "")
                        st.write(text)
                    
                
        

with tab_practice:
    "Practice"

with tab_progress:
    "Progress"
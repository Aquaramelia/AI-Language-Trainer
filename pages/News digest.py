from numpy import select
import streamlit as st
from st_helpers import news_digest_helpers
from st_helpers.news_digest_helpers import save_to_database, return_article, execute_rss_ingestion, return_selectbox_feed_categories
from st_helpers.general_helpers import set_background, load_css
from st_helpers.aggrid_news_digest import display_grid
import pandas as pd

st.set_page_config(
    page_title="News Digest - AI Language Trainer",
    page_icon="📖",
    layout="wide")
set_background()
load_css()
st.title("News Digest")
st.header("Take a look at recent news from real German news feeds and choose some interesting ones!")
st.caption("Articles for practice may differ slighlty from the original ones.")
USER_ID = 1

if "last_feed" not in st.session_state:
    st.session_state.last_feed = ""
if "last_article_displayed" not in st.session_state:
    st.session_state.last_article_displayed = ""
if "last_feed_dataframe" not in st.session_state:
    st.session_state.last_feed_dataframe = ""
if "news_articles" not in st.session_state:
    st.session_state.news_articles = execute_rss_ingestion()

# State of generating new articles
if "feed_retrieval_in_progress" not in st.session_state:
    st.session_state.feed_retrieval_in_progress = False

col1, col2, col3 = st.columns([1, 2, 1])
generation_button_key = "generate-articles-button"

with col2:
    if st.button("Generate new articles! 🗞️", key=generation_button_key, disabled=st.session_state.feed_retrieval_in_progress, use_container_width=True):
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
        key="news-browse-container"
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
                    options=news_digest_helpers.return_selectbox_feed_categories(),
                    label="Select a feed to view news:",
                    index=None
                )
                if selectbox_selection:
                    feed_selection = selectbox_selection

                if feed_selection and feed_selection != st.session_state.last_feed:
                    articles_dict = [return_article(feed_selection, articles) for articles in st.session_state.news_articles[feed_selection]]
                    st.code(f"🔍 Loaded {len(st.session_state.news_articles[feed_selection])} entries from the RSS feed of {feed_selection}")
                    st.toast("Retrieving RSS feed data...", icon="⏳")
                    feed_df = pd.DataFrame(articles_dict)

                    st.session_state.last_feed = feed_selection
                    st.session_state.last_feed_dataframe = feed_df

                if feed_df is not None and type(feed_df) == pd.DataFrame:
                    print(feed_df.head())
                    grid_response = display_grid(feed_df=feed_df, feed_selection=feed_selection)

                    # Get selected row
                    selected = grid_response.selected_rows
                    print(selected)
                    selected_word = ""
                    if selected is not [] and selected is not None:
                        print(selected.iloc[0])
                        selected_article = selected.iloc[0]["title"]
                        if selected_article is not None:
                            st.session_state.last_article_displayed = selected_article
                    else:
                        selected_article = st.session_state.last_article_displayed
                    if selected_article:
                        matching_rows = feed_df[feed_df["title"] == selected_article]
                        if not matching_rows.empty:
                            matching_row = matching_rows.iloc[0]

        with col2:
            if matching_row is not None:
                with st.container(
                    key="news-digest-article-card"
                ):
                    with st.container(
                        key="news-digest-article-title"
                    ):
                        title = matching_row.get("title", "")
                        st.write(title)
                    with st.container(
                        key="news-digest-article-feed-name"
                    ):
                        feed_name = matching_row.get("feed_name", "")
                        st.write(feed_name)
                    with st.container(
                        key="news-digest-article-url"
                    ):
                        url = matching_row.get("url", "")
                        st.write(url)
                    with st.container(
                        key="news-digest-article-published"
                    ):
                        published = matching_row.get("published", "")
                        st.write(published)
                    with st.container(
                        key="news-digest-article-text"
                    ):
                        text = matching_row.get("text", "")
                        st.write(text)
                    
                
        

with tab_practice:
    "Practice"

with tab_progress:
    "Progress"
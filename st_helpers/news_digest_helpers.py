import sqlite3
from news_digest import news_models
from news_digest.ingest_rss import ingest_from_rss
from news_digest.news_models import ArticleItem, RSS_FEEDS
from news_digest.database_helpers import update_article_status
from typing import List, Dict
from dotenv import load_dotenv
import os
import streamlit as st

load_dotenv()
DB_PATH = os.getenv('DATABASE_NEWS_URL', "news_database.db")

def return_article(feed_name: str, article: ArticleItem):
    """
    Return each article as a dictionary of all associated data.
    """
    return {
        "title": article.title,
        "text": article.text,
        "published": article.published,
        "url": article.url,
        "feed_name": feed_name,
        "status": article.status
    }

def update_article(url: str, accepted: bool):
    """
    Update the article's status after the corresponding user action.
    """
    conn = sqlite3.connect(DB_PATH)
    update_article_status(
        conn=conn, 
        url=url, 
        accepted=accepted)
    conn.close()


def execute_rss_ingestion() -> Dict[str,List[ArticleItem]]:
    """
    Retrieve articles from RSS feeds, or cached content, if existing.
    """
    return ingest_from_rss()

def return_selectbox_feed_categories() -> List[str]:
    """
    Return the feed names (keys) from the dictionary of available feeds.
    """
    return [name for feed, name in news_models.RSS_FEEDS.items()]

def shorten_url_for_display(url: str, max_length: int = 50) -> str:
    """
    Shorten the article URL for appearance reasons.
    """
    if len(url) <= max_length:
        return url
    return url[:max_length - 3] + "..."

def display_url(url: str):
    """
    Show the URL shortened + as a hyperlink.
    """
    short = shorten_url_for_display(url)
    st.markdown(f"[{short}]({url})")

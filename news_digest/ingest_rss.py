import os
import sqlite3
import nltk
import feedparser
from typing import Dict, List, Optional
from newspaper import Article
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from trafilatura import fetch_url, extract
import json
from news_digest import news_models
from news_digest.news_models import ArticleItem, RSS_FEEDS
import time
from news_digest.database_helpers import update_last_view_time, get_last_view_time, create_refresh_rss_table, create_articles_table, article_exists, articles_exist, save_article_to_db, get_articles_from_db

# Download NLTK resources
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.data.load('tokenizers/punkt/german.pickle')

# --- Configuration ---
load_dotenv()
DB_PATH = os.getenv('DATABASE_NEWS_URL', "news_database.db")


# --- Article processing using Newspaper3K ---
# def process_entry(entry, feed_name):
#     """
#     Process the entry using the Newspaper3K library 
#     and return the ArticleItem that contains all necessary information.
#     """
#     url = entry.link
#     try:
#         art = Article(url, language='de')
#         art.download()
#         art.parse()
#         if len(art.text.split()) < 50:
#             return None
#         return ArticleItem(
#             title=art.title or entry.get("title", ""),
#             url=url,
#             published=entry.get("published", ""),
#             text=art.text,
#             feed_name=feed_name,
#             status="initial"
#         )
#     except Exception as e:
#         print(f"Error processing {url}: {e}")
#         return None

# def fetch_feed_articles(feed_url: str, feed_name: str) -> List[ArticleItem]:
#     """
#     Fetch RSS articles and process them via Newspaper3K using multiple threads
#     """
#     feed = feedparser.parse(feed_url)
#     entries = feed.entries

#     with ThreadPoolExecutor(max_workers=5) as executor:
#         results = list(executor.map(process_entry, entries, feed_name))
#     article_items = [item for item in results if item is not None]
#     return article_items


# --- Article processing using trafilatura ---
def extract_article_data(url: str) -> dict:
    """
    Extract article data using trafilatura, return the result as a JSON.
    """
    downloaded = fetch_url(url)
    if downloaded:
        result_json = extract(
            downloaded, 
            output_format="json", 
            favor_recall=True,
            include_formatting=True)
        if result_json:
            data = json.loads(result_json)
            if len(data.get("text", "").split()) >= 50:
                return data
    raise ValueError(f"Could not extract article from {url}")


def process_entry_trafilatura(entry, feed_name: str) -> Optional[ArticleItem]:
    """
    Process an article entry using trafilatura, then create the ArticleItem
    with the relevant article information, save it in the database and return it.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        url = entry.get("link")
        if not url or article_exists(conn, url):
            return None

        article_data = extract_article_data(url)
        if not article_data or len(article_data.get("text", "").split()) < 50:
            return None

        article = ArticleItem(
            title=article_data.get("title") or entry.get("title", ""),
            url=url,
            published=article_data.get("date") or entry.get("published", ""),
            text=article_data.get("text", ""),
            feed_name=feed_name,
            status="received"
        )
        
        save_article_to_db(conn, article)
        conn.commit()
        conn.close()
        return article
    except Exception as e:
        print(f"Error processing entry from {entry.get("link")}: {e}")
        return None


def fetch_feed_articles_trafilatura(feed_url: str, feed_name: str, max_items: int = 5) -> List[ArticleItem]:
    """
    Fetch feed articles using trafilatura, then process them in multiple threads to improve response time.
    """
    feed = feedparser.parse(feed_url)
    entries = feed.entries[:max_items]
    with ThreadPoolExecutor(max_workers=5) as executor:        
        results = list(executor.map(lambda entry: process_entry_trafilatura(entry, feed_name), entries))
    return [item for item in results if item]


# --- Main RSS Ingestion ---
def ingest_from_rss() -> Dict[str, List[ArticleItem]]:
    article_items: Dict[str, List[ArticleItem]] = {}
    """
    Main function that handles fetching new RSS articles, if no articles exist 
    or if enough time has passed since the last article retrieval.
    """

    if not articles_exist(DB_PATH) or time.time() - get_last_view_time(DB_PATH) > 3600:
        # render new_articles
        update_last_view_time(DB_PATH)
        for feed_url, feed_name in news_models.RSS_FEEDS.items():
            print(f"Fetching articles from {feed_name} ({feed_url})")
            articles = fetch_feed_articles_trafilatura(feed_url, feed_name)
            if articles:
                article_items[feed_name] = articles
                print(f"Added {len(articles)} articles from {feed_name}")
            else:
                print(f"No valid articles from {feed_name}")
    else:
        article_items = get_articles_from_db(DB_PATH=DB_PATH)

    return article_items

# Always create the table if it doesn't already exist
create_articles_table(DB_PATH)
create_refresh_rss_table(DB_PATH)

if __name__ == '__main__':
    ingest_from_rss()
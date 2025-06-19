import os
import sqlite3
import requests
import nltk
import feedparser
from datetime import datetime
from typing import Dict, List
from transformers import AutoTokenizer, BertForNextSentencePrediction
from bs4 import BeautifulSoup
from newspaper import Article
from nltk.tokenize import sent_tokenize
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

from news_digest import news_models
from news_digest.news_models import ArticleItem, RSS_FEEDS

# Download NLTK resources
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.data.load('tokenizers/punkt/german.pickle')

# --- Configuration ---
load_dotenv()
DB_PATH = os.getenv('DATABASE_NEWS_URL', "news_database.db")
MAX_CHUNK_TOKENS = 3000
MIN_CHUNK_TOKENS = 1500
COHERENCE_THRESHOLD = 0.5
MODEL_NAME = 'bert-base-german-cased'


# --- Database Setup ---
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY,
    title TEXT,
    source_url TEXT,
    published_at TEXT,
    text TEXT
)
''')
conn.commit()
conn.close()

# --- Helpers ---
def process_entry(entry, feed_name):
    url = entry.link
    try:
        art = Article(url, language='de')
        art.download()
        art.parse()
        if len(art.text.split()) < 50:
            return None
        return ArticleItem(
            title=art.title or entry.get("title", ""),
            url=url,
            published=entry.get("published", ""),
            text=art.text,
            feed_name=feed_name
        )
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return None


def fetch_feed_articles(feed_url: str, feed_name: str) -> List[ArticleItem]:
    feed = feedparser.parse(feed_url)
    entries = feed.entries

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_entry, entries, feed_name))
    article_items = [item for item in results if item is not None]

    return article_items

def insert_article_to_db(article: ArticleItem):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO articles
        (title, source_url, published_at, text)
        VALUES (?, ?, ?, ?, ?, ?)''',
        (article.title, article.url, article.published, article.text))
    conn.commit()
    conn.close()

# --- Main Ingestion ---
def ingest_from_rss() -> Dict[str, List[ArticleItem]]:
    article_items: Dict[str, List[ArticleItem]] = {}

    for feed_url, feed_name in news_models.RSS_FEEDS.items():
        print(f"Fetching articles from {feed_name} ({feed_url})")
        articles = fetch_feed_articles(feed_url, feed_name)
        if articles:
            article_items[feed_name] = articles
            print(f"Added {len(articles)} articles from {feed_name}")
        else:
            print(f"No valid articles from {feed_name}")

    return article_items


if __name__ == '__main__':
    ingest_from_rss()
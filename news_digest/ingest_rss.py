import os
import sqlite3
import requests
import nltk
import feedparser
from datetime import datetime
from typing import Dict, List
from transformers import AutoTokenizer, BertForNextSentencePrediction
import torch
from bs4 import BeautifulSoup
from newspaper import Article
from nltk.tokenize import sent_tokenize
from dotenv import load_dotenv

from news_digest import news_models
from news_digest.news_models import ArticleItem, RSS_FEEDS

torch.classes.__path__ = []

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
def fetch_feed_articles(feed_url: str, feed_name: str, max_items: int = 5) -> List[ArticleItem]:
    feed = feedparser.parse(feed_url)
    entries = feed.entries[:max_items]
    article_items = []

    for entry in entries:
        url = entry.link
        try:
            text = extract_text_from_url(url)
            if len(text.split()) < 50:
                continue

            art = Article(url, language='de')
            art.download()
            art.parse()
            title = art.title or entry.get("title", "")

            article_items.append(ArticleItem(
                title = str(art.title or entry.get("title") or ""),
                url = str(entry.get("link") or ""),
                published = str(entry.get("published") or ""),
                text=text,
                feed_name=feed_name
            ))
        except Exception as e:
            print(f"Error processing {url}: {e}")
            continue

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

def extract_text_from_url(url):
    # Use Newspaper3k for robust content extraction
    art = Article(url, language='de')
    art.download()
    art.parse()
    art.nlp() 
    clean_node = art.clean_top_node
    if clean_node is not None:
        text = clean_node.text_content()
    else:
        text = art.text
    return art.text or ''

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
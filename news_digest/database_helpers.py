import sqlite3
import time
from news_digest.news_models import ArticleItem
from typing import List, Dict
from collections import defaultdict

# --- RSS news refresh data ---
def create_refresh_rss_table(DB_PATH:str):
    """
    Create the table that holds the user metadata regarding RSS news retrieval.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS user_meta (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    ''')
    conn.commit()
    conn.close()

def get_last_view_time(DB_PATH:str) -> float:
    """
    Get the time of last RSS news retrieval.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM user_meta WHERE key = 'last_view_time'")
    row = c.fetchone()
    conn.close()
    return float(row[0]) if row else 0.0

def update_last_view_time(DB_PATH:str):
    """
    Store the RSS news retrieval time.
    """
    conn = sqlite3.connect(DB_PATH)
    now = time.time()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO user_meta (key, value) VALUES ('last_view_time', ?)", (str(now),))
    conn.commit()
    conn.close()

# --- Article checks and storage ---
def create_articles_table(DB_PATH:str):
    """
    Create the articles table, if it doesn't already exist, 
    to store the articles retrieved from the RSS feed.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY,
        title TEXT,
        source_url TEXT,
        published_at TEXT,
        text TEXT,
        feed_name TEXT,
        status TEXT
    )
    ''')
    conn.commit()
    conn.close()


def article_exists(conn, url: str) -> bool:
    """
    Check whether the article, defined by its URL, exists in the articles table.
    """
    c = conn.cursor()
    c.execute("SELECT 1 FROM articles WHERE source_url = ?", (url,))
    result = c.fetchone()
    return result is not None

def articles_exist(DB_PATH:str) -> bool:
    """
    Check whether any articles have been stored in the database.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT 1 FROM articles LIMIT 1')
    result = c.fetchone()
    conn.close()
    return result is not None

def save_article_to_db(conn, article: ArticleItem):
    """
    Save the article to the articles table, if it doesn't exist already.
    """
    if article_exists(conn, article.url):
        return
    c = conn.cursor()
    c.execute('''
        INSERT INTO articles (title, source_url, published_at, text, feed_name, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (article.title, article.url, article.published, article.text, article.feed_name, article.status))
    

def get_articles_from_db(DB_PATH: str, limit: int = 10) -> Dict[str,List[ArticleItem]]:
    """
    Retrieve articles already saved in the database, as an ArticleItems list.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT title, source_url, published_at, text, feed_name, status
        FROM articles
        ORDER BY feed_name, published_at DESC
    ''')
    
    rows = c.fetchall()
    grouped_articles = defaultdict(list)

    for row in rows:
        article = ArticleItem(
            title=row[0],
            url=row[1],
            published=row[2],
            text=row[3],
            feed_name=row[4],
            status=row[5]
        )
        grouped_articles[article.feed_name].append(article)

    # Optionally limit the number of articles per feed
    for feed in grouped_articles:
        grouped_articles[feed] = grouped_articles[feed][:limit]

    return dict(grouped_articles)

def update_article_status(conn, url: str, accepted: bool):
    """
    Update the article's status to accepted or rejected 
    after the corresponding user action.
    """
    new_status = "accepted" if accepted else "rejected"
    c = conn.cursor()
    c.execute('''
        UPDATE articles
        SET status = ?
        WHERE source_url = ?
    ''', (new_status, url))
    conn.commit()

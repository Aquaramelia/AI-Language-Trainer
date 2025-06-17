import os
import sqlite3
import requests
import nltk
import feedparser
from datetime import datetime
from transformers import AutoTokenizer, BertForNextSentencePrediction
import torch
from bs4 import BeautifulSoup
from newspaper import Article
from nltk.tokenize import sent_tokenize
from dotenv import load_dotenv

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
# List of German news RSS feeds
RSS_FEEDS = [
    'https://www.tagesschau.de/xml/rss2',
    'https://rss.dw.com/rdf/rss-de-all',
    'https://www.deutschlandfunk.de/podcast-weltweit.3777.de.podcast.xml'
]

# --- Database Setup ---
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY,
    title TEXT,
    source_url TEXT,
    published_at TEXT,
    part_index INTEGER,
    total_parts INTEGER,
    text TEXT
)
''')
c.execute('CREATE INDEX IF NOT EXISTS idx_source_part ON articles(source_url, part_index)')
conn.commit()

# --- Load model & tokenizer ---
print('Loading German BERT model for NSP...')
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, local_files_only=True)
model = BertForNextSentencePrediction.from_pretrained(MODEL_NAME, local_files_only=True)
model.eval()

# --- Article data class ---
class Article:
    title: str
    url: str
    text: str
    author: str
    published: str

# --- Helpers ---
def fetch_feed_articles(feed_url, max_items=5):
    feed = feedparser.parse(feed_url)
    articles = []
    entries = feed.entries[:max_items]
    for entry in entries:
        articles.append({
            'url': entry.link,
            'title': entry.get('title', ''),
            'author': entry.get('author', ''),
            'published': entry.get('published', '')
        })
    return articles

def insert_article_to_db(title, url, published, idx, total, chunk):
    c.execute('''INSERT OR IGNORE INTO articles
        (title, source_url, published_at, part_index, total_parts, text)
        VALUES (?, ?, ?, ?, ?, ?)''',
        (title, url, published, idx, total, chunk))

def confirm_and_store_article(article):
    print("\n========================")
    print(f"📰 Title: {article['title']}")
    print(f"🔗 URL: {article['url']}")
    print(f"✍️  Author: {article['author']}")
    print(f"📅 Published: {article['published']}")
    print("📝 Text:\n")
    print(article['text'])
    print("\n========================")

    confirm = input("Save this article? [y/n] ").strip().lower()
    if confirm == "y":
        insert_article_to_db(
            article['title'], article['url'], article['published'], article['idx'], article['total'], article['text'])
        print("✅ Saved to DB.\n")
    else:
        print("❌ Skipped.\n")

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


def segment_text(text):
    sentences = sent_tokenize(text, language='german')
    chunks, current, current_tokens = [], [], 0
    def flush():
        nonlocal current, current_tokens
        if current:
            chunks.append(' '.join(current))
            current, current_tokens = [], 0

    for sent in sentences:
        tok_count = len(tokenizer.tokenize(sent))
        # check semantics only if current not empty
        if current:
            prev_sent = current[-1]
            enc = tokenizer(prev_sent, sent, return_tensors='pt', truncation="longest_first", max_length=512)
            with torch.no_grad():
                logits = model(**enc).logits
            prob_next = torch.softmax(logits, dim=1)[0, 0].item()
        else:
            prob_next = 1.0

        # decide break: size or coherence
        if (current_tokens + tok_count > MAX_CHUNK_TOKENS and current_tokens >= MIN_CHUNK_TOKENS) or prob_next < COHERENCE_THRESHOLD:
            flush()
        current.append(sent)
        current_tokens += tok_count

    flush()
    # merge last chunk if too small
    if len(chunks) > 1 and len(tokenizer.tokenize(chunks[-1])) < MIN_CHUNK_TOKENS:
        chunks[-2] = chunks[-2] + ' ' + chunks[-1]
        chunks.pop()
    return chunks

# --- Main Ingestion ---
def ingest_from_rss():
    urls = set()
    feed_articles = []
    for feed in RSS_FEEDS:
        fetched = fetch_feed_articles(feed)
        print(f'Fetched {len(fetched)} URLs from {feed}')
        urls.update([f['url'] for f in fetched])
        feed_articles.extend(fetched)

    for article in feed_articles:
        url = article['url']
        try:
            text = extract_text_from_url(url)
            if len(text.split()) < 50:
                continue
            # Download the article to get cleaned title if available
            art = Article(url, language='de')
            art.download()
            art.parse()
            title = art.title or article['title']
            chunks = segment_text(text)
            for idx, chunk in enumerate(chunks, start=1):
                article_data = {
                    'title': title,
                    'url': url,
                    'text': chunk,
                    'author': article.get('author', ''),
                    'published': article.get('published', '')
                }
                confirm_and_store_article(article_data)
        except Exception as e:
            print(f'Error processing {url}: {e}')
    conn.commit()
    print('Total stored chunks:', c.execute('SELECT COUNT(*) FROM articles').fetchone()[0])


if __name__ == '__main__':
    ingest_from_rss()
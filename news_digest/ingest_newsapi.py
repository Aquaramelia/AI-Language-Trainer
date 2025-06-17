import os
import sqlite3
import requests
from datetime import datetime
from transformers import AutoTokenizer, BertForNextSentencePrediction
import torch
import nltk
from nltk.tokenize import sent_tokenize
from dotenv import load_dotenv

# Ensure German punkt models are downloaded
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.data.load('tokenizers/punkt/german.pickle')

# --- Configuration ---
load_dotenv()
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')  # Set your NewsAPI.org key in environment
NEWSAPI_ENDPOINT = 'https://newsapi.org/v2/top-headlines'
DB_PATH = os.getenv('DATABASE_NEWS_URL')
MAX_CHUNK_TOKENS = 300  # approx. number of tokens per chunk
COHERENCE_THRESHOLD = 0.5  # threshold for breaking on low coherence
MODEL_NAME = 'bert-base-german-cased'  # small German model supporting NSP

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
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = BertForNextSentencePrediction.from_pretrained(MODEL_NAME)
model.eval()

def segment_text(text):
    """
    Split German text into semantically coherent chunks using NSP scores.
    """
    # Sentence splitting
    sentences = sent_tokenize(text, language='german')
    chunks = []
    current = []
    current_tokens = 0

    def flush_chunk():
        nonlocal current, current_tokens
        if current:
            chunks.append(' '.join(current))
            current = []
            current_tokens = 0

    for i, sent in enumerate(sentences):
        # count tokens
        tok_count = len(tokenizer.tokenize(sent))
        # decide to break? check coherence with previous sentence
        break_for_coherence = False
        if current and i < len(sentences):
            prev = current[-1]
            encoding = tokenizer(prev, sent, return_tensors='pt', truncation=True)
            with torch.no_grad():
                scores = model(**encoding).logits
            # logits: [is_next_sentence, is_random_sentence]
            # probability that it's next sentence
            prob = torch.softmax(scores, dim=1)[0, 0].item()
            if prob < COHERENCE_THRESHOLD:
                break_for_coherence = True
        # if adding exceeds max or coherence dropped, flush
        if break_for_coherence or current_tokens + tok_count > MAX_CHUNK_TOKENS:
            flush_chunk()
        # append sentence
        current.append(sent)
        current_tokens += tok_count
    # final flush
    flush_chunk()
    return chunks

# --- Fetch German news via API ---
def fetch_latest_german_headlines(country='de', page_size=20, category='science', query='plant'):
    """Fetch recent German news headlines from NewsAPI."""
    params = {
        'apiKey': NEWSAPI_KEY,
        # 'q': query,
        # 'category': category,
        'pageSize': page_size,
        'country': country,
    }
    resp = requests.get(NEWSAPI_ENDPOINT, params=params)
    resp.raise_for_status()
    data = resp.json()
    print(resp.content)
    return data.get('articles', [])

# --- Ingest pipeline ---
def ingest_articles():
    articles = fetch_latest_german_headlines()
    for art in articles:
        url = art['url']
        title = art.get('title') or url
        published = art.get('publishedAt')
        # combine available text pieces
        content = art.get('content') or art.get('description') or ''
        if not content:
            continue
        # segment
        chunks = segment_text(content)
        total = len(chunks)
        # insert into DB
        for idx, chunk in enumerate(chunks, 1):
            c.execute('''INSERT OR IGNORE INTO articles
                         (title, source_url, published_at, part_index, total_parts, text)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (title, url, published, idx, total, chunk))
    conn.commit()
    print(f'Ingested {len(articles)} articles into DB.')

if __name__ == '__main__':
    ingest_articles()

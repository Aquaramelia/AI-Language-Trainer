from dataclasses import dataclass
from typing import Dict

# --- Article data class ---
@dataclass
class ArticleItem:
    title: str
    url: str
    text: str
    published: str
    feed_name: str

# List of German news RSS feeds
RSS_FEEDS: Dict[str,str] = {
    'https://www.tagesschau.de/xml/rss2': "Tagesschau",
    'https://rss.dw.com/rdf/rss-de-all': "Deutsche Welle"
}
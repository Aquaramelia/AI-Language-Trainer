from news_digest import news_models
from news_digest.ingest_rss import ingest_from_rss, insert_article_to_db
from news_digest.news_models import ArticleItem, RSS_FEEDS
from typing import List, Dict

def return_article(feed_name: str, article: ArticleItem):
    return {
        "title": article.title,
        "text": article.text,
        "published": article.published,
        "url": article.url,
        "feed_name": feed_name
    }

def save_to_database(article: ArticleItem):
    insert_article_to_db(article)

def execute_rss_ingestion() -> Dict[str,List[ArticleItem]]:
    return ingest_from_rss()

def return_selectbox_feed_categories() -> List[str]:
    return [name for feed, name in news_models.RSS_FEEDS.items()]
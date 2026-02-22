# app/utils/feed_fetcher.py
import feedparser
from datetime import datetime
from app import db
from app.models import Feed, Article


def fetch_feed(feed_url):
    """
    抓取单个 RSS 源，返回新文章列表
    """
    parsed = feedparser.parse(feed_url)
    new_articles = []

    # 查找对应的 Feed 记录（假设已存在）
    feed = Feed.query.filter_by(url=feed_url).first()
    if not feed:
        # 如果 feed 不存在，可以抛出异常或返回空
        return []

    for entry in parsed.entries:
        # 检查文章是否已存在（通过链接去重）
        existing = Article.query.filter_by(link=entry.link).first()
        if existing:
            continue

        # 解析发布时间（不同 RSS 格式字段不同，常见有 published、pubDate、updated）
        published = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6])
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            published = datetime(*entry.updated_parsed[:6])

        # 创建新文章
        article = Article(
            title=entry.get('title', '无标题'),
            link=entry.link,
            published=published,
            summary=entry.get('summary', ''),
            is_read=False,
            feed_id=feed.id
        )
        db.session.add(article)
        new_articles.append(article)

    db.session.commit()
    return new_articles


def fetch_all_feeds():
    """
    抓取所有订阅源（用于定时任务）
    """
    """抓取所有订阅源的最新文章"""
    feeds = Feed.query.all()
    for feed in feeds:
        try:
            fetch_feed(feed.url)
            print(f"已抓取: {feed.name}")
        except Exception as e:
            print(f"抓取失败 {feed.name}: {e}")
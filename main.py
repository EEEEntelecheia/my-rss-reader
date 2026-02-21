import feedparser

# rss解析脚本
if __name__ == "__main__":
    feed = feedparser.parse("https://www.ithome.com/rss/")
    for entry in feed.entries[:5]:
        print(entry.title)

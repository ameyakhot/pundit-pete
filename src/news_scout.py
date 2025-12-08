import feedparser
from datetime import datetime, timedelta
import time

# Google News RSS URL for specific query
RSS_URL = "https://news.google.com/rss/search?q=National+Quantum+Mission+India+OR+Department+of+Science+and+Technology+Quantum&hl=en-IN&gl=IN&ceid=IN:en"

def fetch_news(hours=168): # Changed default to 7 days (168 hours)
    """
    Fetches news from Google News RSS feed about National Quantum Mission.
    Returns a list of dictionaries containing title, link, and published date.
    Filters articles published within the last `hours`.
    """
    print(f"Fetching news from {RSS_URL}...")
    feed = feedparser.parse(RSS_URL)
    
    articles = []
    current_time = datetime.now()
    
    # Time threshold
    threshold_time = current_time - timedelta(hours=hours)
    
    print(f"Found {len(feed.entries)} entries. Filtering for last {hours} hours...")

    for entry in feed.entries:
        # Parse published date
        if entry.get("published_parsed"):
            published_dt = datetime.fromtimestamp(time.mktime(entry.published_parsed))
            
            if published_dt >= threshold_time:
                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": published_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "source": entry.source.title if hasattr(entry, "source") else "Unknown",
                    "id": entry.id if hasattr(entry, "id") else entry.link
                })
    
    print(f"Found {len(articles)} relevant articles.")
    return articles

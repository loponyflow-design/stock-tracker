"""News fetchers, shared between news_alert.py and the AI news team pipeline.

Moved out of news_alert.py so both scripts call the same fetch logic instead
of duplicating it. Unlike news_alert.py itself, these take their API key as a
parameter rather than reading a module-level env var — importing this module
doesn't force FINNHUB_KEY/TG_TOKEN/TG_CHAT to be set the way importing
news_alert.py would.

Both functions return a normalized shape regardless of source:
    {"headline": str, "url": str, "summary": str, "ts_label": str}
so callers (classify_ticker_news) don't need market-specific parsing.
"""
from datetime import datetime, timezone

import feedparser
import requests
from urllib.parse import quote


def fetch_finnhub_news(ticker: str, since: datetime, now: datetime, api_key: str) -> list:
    resp = requests.get(
        "https://finnhub.io/api/v1/company-news",
        params={"symbol": ticker, "from": since.strftime("%Y-%m-%d"),
                "to": now.strftime("%Y-%m-%d"), "token": api_key},
        timeout=10,
    )
    resp.raise_for_status()
    articles = resp.json()[:5]
    return [
        {
            "headline": a.get("headline", ""),
            "url": a.get("url", ""),
            "summary": a.get("summary", ""),
            "ts_label": datetime.fromtimestamp(a["datetime"], tz=timezone.utc).strftime("%H:%M UTC")
            if a.get("datetime") else "",
        }
        for a in articles
    ]


def fetch_google_news(query: str) -> list:
    url = f"https://news.google.com/rss/search?q={quote(query)}&hl=th-TH&gl=TH&ceid=TH:th"
    feed = feedparser.parse(url)
    return [
        {
            "headline": e.title,
            "url": e.link,
            "summary": getattr(e, "summary", ""),
            "ts_label": "",
        }
        for e in feed.entries[:5]
    ]

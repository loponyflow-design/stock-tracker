"""Phase 1 category: stocks/economy digest.

Reuses news_alert.py's own fetch + brief-signal-match logic (via the shared
sources/news_fetch.py and match/signal_match.py modules) against the DCA
holdings ticker universe — no separate inbound source, since news_alert.py
already fetches news directly from Finnhub/Google News itself.

Adding a future category (world news, health research, food/business
trends) means writing a new file like this one with its own `collect_items`
and output env vars — run_category.py doesn't change.
"""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ai_news_team.match.signal_match import classify_ticker_news
from ai_news_team.sources.news_fetch import fetch_finnhub_news, fetch_google_news

try:
    # scripts/ is on sys.path when this runs (same trick news_alert.py uses).
    from tickers import TH_SET, us_tickers
except ImportError:
    TH_SET, us_tickers = set(), None

DCA_JSON_PATH = "webapp/dca.json"


def _load_tickers() -> list:
    """Ticker universe for matching. Prefers the DCA holdings written earlier
    in the same job by gen_dca_json.py (no second Web App call needed); falls
    back to the briefs-derived list if that file is missing or unreadable."""
    dca_path = Path(DCA_JSON_PATH)
    if dca_path.exists():
        try:
            data = json.loads(dca_path.read_text(encoding="utf-8"))
            tickers = [h["ticker"] for h in data.get("holdings", []) if h.get("ticker")]
            if tickers:
                return tickers
        except Exception as e:
            print(f"stocks.collect_items: failed to read {dca_path}, falling back: {e}")

    if us_tickers:
        return [s["ticker"] for s in us_tickers()]
    return []


def collect_items(finnhub_key: str, max_items: int = 50) -> list:
    """Fetch + classify today's news for every DCA-held ticker. Returns the
    flattened, capped list of classify_ticker_news() items across tickers —
    the same "ข่าวที่ match แล้ว" data structure news_alert.py itself works
    with, just not yet sent anywhere."""
    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=24)

    all_items = []
    for ticker in _load_tickers():
        market = "TH" if ticker in TH_SET else "US"
        articles = (fetch_finnhub_news(ticker, since, now, finnhub_key) if market == "US"
                    else fetch_google_news(f"{ticker} stock SET"))
        all_items.extend(classify_ticker_news(ticker, market, articles))

    return all_items[:max_items]


CATEGORY = {
    "name": "stocks",
    "output_bot_token_env": "TG_TOKEN",
    "output_chat_id_env": "TG_CHAT",
    "finnhub_key_env": "FINNHUB_KEY",
    "max_items": 50,
    "collect_items": collect_items,
}

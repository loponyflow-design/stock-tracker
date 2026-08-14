#!/usr/bin/env python3
import os, json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from tickers import TH_TICKERS, us_tickers
from ai_news_team.telegram_send import send_telegram_chunks
from ai_news_team.sources.news_fetch import fetch_finnhub_news, fetch_google_news
from ai_news_team.match.signal_match import classify_ticker_news

FINNHUB_KEY = os.environ["FINNHUB_KEY"]
TG_TOKEN    = os.environ["TG_TOKEN"]
TG_CHAT     = int(os.environ["TG_CHAT"])

US_TICKERS = [s["ticker"] for s in us_tickers()]


# ── Telegram ──────────────────────────────────────────────────────────────

def send_telegram(text: str):
    send_telegram_chunks(text, TG_TOKEN, TG_CHAT)


# ── alerts json (bear + bull) ───────────────────────────────────────────────

def update_alerts_json(path_str: str, new_alerts: dict, now: datetime):
    path = Path(path_str)
    existing: dict = {}
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8")).get("alerts", {})
        except Exception:
            pass

    # Merge new + existing, keep max 5 per ticker
    for ticker, alerts in new_alerts.items():
        existing.setdefault(ticker, [])
        existing[ticker] = (alerts + existing[ticker])[:5]

    # Purge alerts older than 7 days
    cutoff = (now - timedelta(days=7)).isoformat()
    for ticker in list(existing.keys()):
        existing[ticker] = [a for a in existing[ticker] if a.get("detected_at", "") > cutoff]
        if not existing[ticker]:
            del existing[ticker]

    path.write_text(
        json.dumps({"last_updated": now.isoformat(), "alerts": existing},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ── Main ──────────────────────────────────────────────────────────────────

def _dispatch_ticker_items(items: list, news_header: str, bull_header: str, bear_header: str,
                            now: datetime, new_bear_alerts: dict, new_bull_alerts: dict) -> tuple:
    """Turn classify_ticker_news()'s output into the same Telegram messages
    and alert-json entries news_alert.py has always sent, and dispatch them.
    `*_header` already includes the trailing date string and blank line."""
    news_lines, bull_signal_lines, bear_lines = [], [], []

    for item in items:
        ticker, headline, url, ts_label = item["ticker"], item["headline"], item["url"], item["ts_label"]
        signal_type, condition = item["signal_type"], item["condition"]

        if signal_type == "bear":
            bear_lines += [f"📰 {headline}{' [' + ts_label + ']' if ts_label else ''}",
                           f"🔗 <a href='{url}'>Verify</a>", f"📌 <i>{condition[:120]}</i>", ""]
            new_bear_alerts.setdefault(ticker, []).append(
                {"headline": headline, "url": url, "condition": condition, "detected_at": now.isoformat()}
            )
        elif signal_type == "bull":
            bull_signal_lines += [f"📰 {headline}{' [' + ts_label + ']' if ts_label else ''}",
                                  f"🔗 <a href='{url}'>Read more</a>", f"📌 <i>{condition[:120]}</i>", ""]
            new_bull_alerts.setdefault(ticker, []).append(
                {"headline": headline, "url": url, "condition": condition, "detected_at": now.isoformat()}
            )
        else:
            news_lines += ([f"[{ts_label}] • {headline}", f"  <a href='{url}'>Read more</a>", ""] if ts_label
                           else [f"• {headline}", f"  <a href='{url}'>Read more</a>", ""])

    if news_lines:
        send_telegram(news_header + "\n".join(news_lines))
    if bull_signal_lines:
        send_telegram(bull_header + "\n".join(bull_signal_lines))
    if bear_lines:
        send_telegram(bear_header + "\n".join(bear_lines))

    return (sum(1 for i in items if i["signal_type"] == "news"),
            sum(1 for i in items if i["signal_type"] == "bull"),
            sum(1 for i in items if i["signal_type"] == "bear"))


def process_ticker_us(ticker: str, since: datetime, now: datetime, date_str: str,
                       new_bear_alerts: dict, new_bull_alerts: dict) -> tuple:
    articles = fetch_finnhub_news(ticker, since, now, FINNHUB_KEY)
    items = classify_ticker_news(ticker, "US", articles)

    return _dispatch_ticker_items(
        items,
        news_header=f"🇺🇸 <b>${ticker}</b> — {date_str}\n\n",
        bull_header=f"🟢 <b>BULL SIGNAL — ${ticker}</b> — {date_str}\n\n",
        bear_header=f"⚠️ <b>BEAR ALERT — ${ticker}</b> — {date_str}\n\n",
        now=now, new_bear_alerts=new_bear_alerts, new_bull_alerts=new_bull_alerts,
    )


def process_ticker_th(stock: dict, now: datetime, date_str: str,
                       new_bear_alerts: dict, new_bull_alerts: dict) -> tuple:
    ticker, name = stock["ticker"], stock["name"]
    articles = fetch_google_news(f"{ticker} stock SET")
    items = classify_ticker_news(ticker, "TH", articles)

    return _dispatch_ticker_items(
        items,
        news_header=f"🇹🇭 <b>{ticker}</b> ({name}) — {date_str}\n\n",
        bull_header=f"🟢 <b>BULL SIGNAL — {ticker}</b> ({name}) — {date_str}\n\n",
        bear_header=f"⚠️ <b>BEAR ALERT — {ticker}</b> ({name}) — {date_str}\n\n",
        now=now, new_bear_alerts=new_bear_alerts, new_bull_alerts=new_bull_alerts,
    )


def main():
    now      = datetime.now(timezone.utc)
    since    = now - timedelta(hours=24)
    date_str = now.strftime("%d %b %Y")
    new_bear_alerts: dict = {}
    new_bull_alerts: dict = {}
    n_news = n_bull = n_bear = 0

    for ticker in US_TICKERS:
        r, bu, be = process_ticker_us(ticker, since, now, date_str, new_bear_alerts, new_bull_alerts)
        n_news += r; n_bull += bu; n_bear += be

    for stock in TH_TICKERS:
        r, bu, be = process_ticker_th(stock, now, date_str, new_bear_alerts, new_bull_alerts)
        n_news += r; n_bull += bu; n_bear += be

    update_alerts_json("webapp/bear_alerts.json", new_bear_alerts, now)
    update_alerts_json("webapp/bull_alerts.json", new_bull_alerts, now)
    print(f"Done — news: {n_news}, bull signals: {n_bull}, bear alerts: {n_bear}")


if __name__ == "__main__":
    main()

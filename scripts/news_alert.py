#!/usr/bin/env python3
import os, re, json, requests, feedparser
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import quote

FINNHUB_KEY = os.environ["FINNHUB_KEY"]
TG_TOKEN    = os.environ["TG_TOKEN"]
TG_CHAT     = int(os.environ["TG_CHAT"])

US_TICKERS = ["AAPL", "ARM", "CVX", "GOOGL", "MSFT", "NVDA", "O", "SPCX", "TSLA"]
TH_TICKERS = [
    {"ticker": "PTT",   "name": "ปตท."},
    {"ticker": "KBANK", "name": "กสิกรไทย"},
    {"ticker": "AOT",   "name": "ท่าอากาศยานไทย"},
]

# ── Bear signal extraction ─────────────────────────────────────────────────

def load_bear_signals(ticker: str) -> dict:
    """Extract keywords from Bear Case + Kill Conditions sections of brief."""
    brief = Path(f"briefs/{ticker}.md")
    if not brief.exists():
        return {"conditions": [], "keywords": []}

    content = brief.read_text(encoding="utf-8")

    # Bear Case bullets
    bear_match = re.search(r'\*\*Bear\*\*\n((?:- .+\n?)+)', content)
    bear_text  = bear_match.group(1) if bear_match else ""

    # Kill Conditions section (has the clearest bold keywords)
    kill_match = re.search(r'## 5\. Kill conditions.*?\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    kill_text  = kill_match.group(1) if kill_match else ""

    combined = bear_text + "\n" + kill_text

    # Conditions: clean bullet text from bear section
    conditions = [
        re.sub(r'\*\*(.+?)\*\*', r'\1', b.lstrip('- ').strip())
        for b in bear_text.strip().split('\n')
        if b.strip().startswith('-')
    ]

    # Keywords: bold phrases + English acronyms (NPL, NIM, LNG, etc.)
    keywords = re.findall(r'\*\*([^*\n]+)\*\*', combined)
    keywords += re.findall(r'\b[A-Z]{2,}\b', combined)

    return {
        "conditions": conditions,
        "keywords": list(set(k.strip() for k in keywords if len(k.strip()) > 2)),
    }


def check_bear(headline: str, summary: str, signals: dict) -> tuple[bool, str]:
    """Returns (is_bear_related, matched_condition_text)."""
    if not signals["keywords"]:
        return False, ""

    text = (headline + " " + (summary or "")).lower()

    for kw in signals["keywords"]:
        kw_lo = kw.lower()

        # Direct substring match (works well for English terms & short Thai phrases)
        if len(kw_lo) > 3 and kw_lo in text:
            matched_cond = next(
                (c for c in signals["conditions"] if kw_lo in c.lower()),
                signals["conditions"][0] if signals["conditions"] else kw,
            )
            return True, matched_cond

        # Word-level match for longer Thai phrases (require ≥2 words to match)
        words = [w for w in re.split(r'[\s,—–\-]+', kw_lo) if len(w) > 3]
        if len(words) >= 2 and sum(1 for w in words if w in text) >= 2:
            matched_cond = next(
                (c for c in signals["conditions"] if any(w in c.lower() for w in words)),
                signals["conditions"][0] if signals["conditions"] else kw,
            )
            return True, matched_cond

    return False, ""


# ── News fetching ──────────────────────────────────────────────────────────

def fetch_finnhub_news(ticker: str, since: datetime, now: datetime) -> list:
    resp = requests.get(
        "https://finnhub.io/api/v1/company-news",
        params={"symbol": ticker, "from": since.strftime("%Y-%m-%d"),
                "to": now.strftime("%Y-%m-%d"), "token": FINNHUB_KEY},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()[:5]


def fetch_google_news(query: str) -> list:
    url  = f"https://news.google.com/rss/search?q={quote(query)}&hl=th-TH&gl=TH&ceid=TH:th"
    feed = feedparser.parse(url)
    return feed.entries[:5]


# ── Telegram ──────────────────────────────────────────────────────────────

def send_telegram(text: str):
    requests.post(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
        json={"chat_id": TG_CHAT, "text": text, "parse_mode": "HTML"},
        timeout=10,
    ).raise_for_status()


# ── bear_alerts.json ───────────────────────────────────────────────────────

def update_bear_json(new_alerts: dict, now: datetime):
    path = Path("webapp/bear_alerts.json")
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

def main():
    now      = datetime.now(timezone.utc)
    since    = now - timedelta(hours=24)
    date_str = now.strftime("%d %b %Y")

    regular_lines = [f"📰 <b>Stock News — {date_str}</b>\n"]
    bear_lines    = []
    new_bear_alerts: dict = {}
    n_regular = n_bear = 0

    # US stocks via Finnhub
    for ticker in US_TICKERS:
        signals  = load_bear_signals(ticker)
        articles = fetch_finnhub_news(ticker, since, now)
        for a in articles:
            ts       = datetime.fromtimestamp(a["datetime"], tz=timezone.utc).strftime("%H:%M UTC")
            headline = a.get("headline", "")
            url      = a.get("url", "")
            summary  = a.get("summary", "")

            is_bear, condition = check_bear(headline, summary, signals)

            if is_bear:
                bear_lines += [
                    f"⚠️ <b>BEAR ALERT — ${ticker}</b> [{ts}]",
                    f"📰 {headline}",
                    f"🔗 <a href='{url}'>ตรวจสอบ</a>",
                    f"📌 <i>{condition[:120]}</i>\n",
                ]
                new_bear_alerts.setdefault(ticker, []).append(
                    {"headline": headline, "url": url,
                     "condition": condition, "detected_at": now.isoformat()}
                )
                n_bear += 1
            else:
                regular_lines += [
                    f"🇺🇸 <b>${ticker}</b> [{ts}]",
                    f"• {headline}",
                    f"  <a href='{url}'>อ่านต่อ</a>\n",
                ]
                n_regular += 1

    # Thai stocks via Google News
    for stock in TH_TICKERS:
        ticker   = stock["ticker"]
        signals  = load_bear_signals(ticker)
        entries  = fetch_google_news(f"{ticker} หุ้น")
        for e in entries:
            headline = e.title
            url      = e.link
            summary  = getattr(e, "summary", "")

            is_bear, condition = check_bear(headline, summary, signals)

            if is_bear:
                bear_lines += [
                    f"⚠️ <b>BEAR ALERT — {ticker}</b> ({stock['name']})",
                    f"📰 {headline}",
                    f"🔗 <a href='{url}'>ตรวจสอบ</a>",
                    f"📌 <i>{condition[:120]}</i>\n",
                ]
                new_bear_alerts.setdefault(ticker, []).append(
                    {"headline": headline, "url": url,
                     "condition": condition, "detected_at": now.isoformat()}
                )
                n_bear += 1
            else:
                regular_lines += [
                    f"🇹🇭 <b>{ticker}</b> ({stock['name']})",
                    f"• {headline}",
                    f"  <a href='{url}'>อ่านต่อ</a>\n",
                ]
                n_regular += 1

    # Send messages
    if n_regular > 0:
        send_telegram("\n".join(regular_lines))

    if n_bear > 0:
        send_telegram(f"🚨 <b>BEAR ALERTS — {date_str}</b>\n\n" + "\n".join(bear_lines))

    # Update bear_alerts.json
    update_bear_json(new_bear_alerts, now)
    print(f"Done — regular: {n_regular}, bear alerts: {n_bear}")


if __name__ == "__main__":
    main()

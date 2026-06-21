#!/usr/bin/env python3
import os, re, json, requests, feedparser
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import quote

FINNHUB_KEY = os.environ["FINNHUB_KEY"]
TG_TOKEN    = os.environ["TG_TOKEN"]
TG_CHAT     = int(os.environ["TG_CHAT"])

US_TICKERS = ["AAPL", "ABBV", "ARM", "BRK.B", "COST", "CVX", "GOOGL", "HEI.A", "JNJ", "KO",
              "MSFT", "NVDA", "O", "PG", "SPCX", "TSLA", "V"]
TH_TICKERS = [
    {"ticker": "PTT",   "name": "ปตท."},
    {"ticker": "KBANK", "name": "กสิกรไทย"},
    {"ticker": "AOT",   "name": "ท่าอากาศยานไทย"},
]

# ── Signal extraction ─────────────────────────────────────────────────────

def _extract_section(content: str, label: str) -> str:
    m = re.search(rf'\*\*{label}\*\*\n((?:- .+\n?)+)', content)
    return m.group(1) if m else ""

def _build_signals(section_text: str, extra_text: str = "") -> dict:
    combined   = section_text + "\n" + extra_text
    conditions = [
        re.sub(r'\*\*(.+?)\*\*', r'\1', b.lstrip('- ').strip())
        for b in section_text.strip().split('\n') if b.strip().startswith('-')
    ]
    keywords  = re.findall(r'\*\*([^*\n]+)\*\*', combined)
    keywords += re.findall(r'\b[A-Z]{2,}\b', combined)
    return {
        "conditions": conditions,
        "keywords": list(set(k.strip() for k in keywords if len(k.strip()) > 2)),
    }

def load_signals(ticker: str) -> dict:
    """Return {"bull": ..., "bear": ...} extracted from brief."""
    empty = {"conditions": [], "keywords": []}
    brief = Path(f"briefs/{ticker}.md")
    if not brief.exists():
        return {"bull": empty, "bear": empty}

    content    = brief.read_text(encoding="utf-8")
    bull_text  = _extract_section(content, "Bull")
    bear_text  = _extract_section(content, "Bear")
    kill_match = re.search(r'## 5\. Kill conditions.*?\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    kill_text  = kill_match.group(1) if kill_match else ""

    return {
        "bull": _build_signals(bull_text),
        "bear": _build_signals(bear_text, kill_text),
    }


def check_signal(headline: str, summary: str, signals: dict) -> tuple[bool, str]:
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
    # Split at article boundaries (\n\n) so each chunk stays under Telegram's 4096-char limit
    LIMIT = 3800
    if len(text) <= LIMIT:
        chunks = [text]
    else:
        chunks, current = [], ""
        for para in text.split("\n\n"):
            candidate = (current + "\n\n" + para).lstrip("\n") if current else para
            if len(candidate) > LIMIT:
                if current:
                    chunks.append(current)
                current = para
            else:
                current = candidate
        if current:
            chunks.append(current)

    for chunk in chunks:
        r = requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={"chat_id": TG_CHAT, "text": chunk, "parse_mode": "HTML"},
            timeout=10,
        )
        print(r.text)
        r.raise_for_status()


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

def _classify_article(headline: str, url: str, summary: str, ts_label: str,
                       signals: dict, ticker: str, now: datetime,
                       new_bear_alerts: dict, new_bull_alerts: dict,
                       news_lines: list, bull_signal_lines: list, bear_lines: list):
    is_bear, bear_cond = check_signal(headline, summary, signals["bear"])
    if is_bear:
        bear_lines += [f"📰 {headline}{' [' + ts_label + ']' if ts_label else ''}", f"🔗 <a href='{url}'>ตรวจสอบ</a>", f"📌 <i>{bear_cond[:120]}</i>", ""]
        new_bear_alerts.setdefault(ticker, []).append(
            {"headline": headline, "url": url, "condition": bear_cond, "detected_at": now.isoformat()}
        )
        return

    is_bull, bull_cond = check_signal(headline, summary, signals["bull"])
    if is_bull:
        bull_signal_lines += [f"📰 {headline}{' [' + ts_label + ']' if ts_label else ''}", f"🔗 <a href='{url}'>อ่านต่อ</a>", f"📌 <i>{bull_cond[:120]}</i>", ""]
        new_bull_alerts.setdefault(ticker, []).append(
            {"headline": headline, "url": url, "condition": bull_cond, "detected_at": now.isoformat()}
        )
        return

    news_lines += ([f"[{ts_label}] • {headline}", f"  <a href='{url}'>อ่านต่อ</a>", ""] if ts_label
                   else [f"• {headline}", f"  <a href='{url}'>อ่านต่อ</a>", ""])


def process_ticker_us(ticker: str, since: datetime, now: datetime, date_str: str, new_bear_alerts: dict, new_bull_alerts: dict) -> tuple[int, int, int]:
    signals  = load_signals(ticker)
    articles = fetch_finnhub_news(ticker, since, now)
    news_lines, bull_signal_lines, bear_lines = [], [], []

    for a in articles:
        ts = datetime.fromtimestamp(a["datetime"], tz=timezone.utc).strftime("%H:%M UTC")
        _classify_article(a.get("headline", ""), a.get("url", ""), a.get("summary", ""),
                          ts, signals, ticker, now, new_bear_alerts, new_bull_alerts,
                          news_lines, bull_signal_lines, bear_lines)

    if news_lines:
        send_telegram(f"🇺🇸 <b>${ticker}</b> — {date_str}\n\n" + "\n".join(news_lines))
    if bull_signal_lines:
        send_telegram(f"🟢 <b>BULL SIGNAL — ${ticker}</b> — {date_str}\n\n" + "\n".join(bull_signal_lines))
    if bear_lines:
        send_telegram(f"⚠️ <b>BEAR ALERT — ${ticker}</b> — {date_str}\n\n" + "\n".join(bear_lines))

    return len(news_lines) // 3, len(bull_signal_lines) // 4, len(bear_lines) // 4


def process_ticker_th(stock: dict, now: datetime, date_str: str, new_bear_alerts: dict, new_bull_alerts: dict) -> tuple[int, int, int]:
    ticker   = stock["ticker"]
    name     = stock["name"]
    signals  = load_signals(ticker)
    entries  = fetch_google_news(f"{ticker} หุ้น")
    news_lines, bull_signal_lines, bear_lines = [], [], []

    for e in entries:
        _classify_article(e.title, e.link, getattr(e, "summary", ""),
                          "", signals, ticker, now, new_bear_alerts, new_bull_alerts,
                          news_lines, bull_signal_lines, bear_lines)

    if news_lines:
        send_telegram(f"🇹🇭 <b>{ticker}</b> ({name}) — {date_str}\n\n" + "\n".join(news_lines))
    if bull_signal_lines:
        send_telegram(f"🟢 <b>BULL SIGNAL — {ticker}</b> ({name}) — {date_str}\n\n" + "\n".join(bull_signal_lines))
    if bear_lines:
        send_telegram(f"⚠️ <b>BEAR ALERT — {ticker}</b> ({name}) — {date_str}\n\n" + "\n".join(bear_lines))

    return len(news_lines) // 3, len(bull_signal_lines) // 4, len(bear_lines) // 4


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

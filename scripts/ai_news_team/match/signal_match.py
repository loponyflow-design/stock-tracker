"""Brief-driven bull/bear signal matching, shared between news_alert.py and
the AI news team pipeline.

`_extract_section`, `_build_signals`, `load_signals`, and `check_signal` are
moved verbatim out of news_alert.py (no logic changes — these never had an
env-var dependency, so moving them is purely for reuse, not decoupling).

`classify_ticker_news` is new: a pure function that turns a normalized
article list into "ข่าวที่ match แล้ว" as plain data — no Telegram sends, no
alert-json mutation — which is what both news_alert.py and the AI news team
orchestrator need.
"""
import re
from pathlib import Path


def _extract_section(content: str, label: str) -> str:
    m = re.search(rf'\*\*{label}\*\*\n((?:- .+\n?)+)', content)
    return m.group(1) if m else ""


def _build_signals(section_text: str, extra_text: str = "") -> dict:
    combined = section_text + "\n" + extra_text
    conditions = [
        re.sub(r'\*\*(.+?)\*\*', r'\1', b.lstrip('- ').strip())
        for b in section_text.strip().split('\n') if b.strip().startswith('-')
    ]
    keywords = re.findall(r'\*\*([^*\n]+)\*\*', combined)
    keywords += re.findall(r'\b[A-Z]{2,}\b', combined)
    return {
        "conditions": conditions,
        "keywords": list(set(k.strip() for k in keywords if len(k.strip()) > 2)),
    }


def load_signals(ticker: str, briefs_dir: str = "briefs") -> dict:
    """Return {"bull": ..., "bear": ...} extracted from the ticker's brief."""
    empty = {"conditions": [], "keywords": []}
    brief = Path(briefs_dir) / f"{ticker}.md"
    if not brief.exists():
        return {"bull": empty, "bear": empty}

    content = brief.read_text(encoding="utf-8")
    bull_text = _extract_section(content, "Bull")
    bear_text = _extract_section(content, "Bear")
    kill_match = re.search(r'## 5\. Kill conditions.*?\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    kill_text = kill_match.group(1) if kill_match else ""

    return {
        "bull": _build_signals(bull_text),
        "bear": _build_signals(bear_text, kill_text),
    }


def check_signal(headline: str, summary: str, signals: dict) -> tuple:
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


def classify_ticker_news(ticker: str, market: str, articles: list) -> list:
    """Classify normalized articles (from sources/news_fetch.py) for one
    ticker against its brief's bull/bear signals — same precedence
    news_alert.py uses (bear checked before bull). Pure: no Telegram sends,
    no alert-json mutation.

    `articles`: [{"headline", "url", "summary", "ts_label"}, ...]
    Returns: [{"ticker", "market", "headline", "url", "summary", "ts_label",
               "signal_type": "bear"|"bull"|"news", "condition"}, ...]
    """
    signals = load_signals(ticker)
    out = []
    for a in articles:
        headline, url, summary, ts_label = a["headline"], a["url"], a["summary"], a["ts_label"]
        base = {"ticker": ticker, "market": market, "headline": headline,
                "url": url, "summary": summary, "ts_label": ts_label}

        is_bear, bear_cond = check_signal(headline, summary, signals["bear"])
        if is_bear:
            out.append({**base, "signal_type": "bear", "condition": bear_cond})
            continue

        is_bull, bull_cond = check_signal(headline, summary, signals["bull"])
        if is_bull:
            out.append({**base, "signal_type": "bull", "condition": bull_cond})
            continue

        out.append({**base, "signal_type": "news", "condition": ""})
    return out

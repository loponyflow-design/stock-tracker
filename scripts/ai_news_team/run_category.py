"""Category-agnostic orchestrator: collect -> summarize -> format -> send.

Takes a CATEGORY config dict (see categories/stocks.py) and runs the
pipeline end to end. Adding a new news category means writing a new
category config with its own `collect_items`, not touching this file.
"""
import os
from datetime import datetime, timezone

from ai_news_team.summarize.claude_summarize import summarize
from ai_news_team.telegram_send import send_telegram_chunks

_SIGNAL_RANK = {"bear": 0, "bull": 1, "neutral": 2}
_SIGNAL_EMOJI = {"bear": "⚠️", "bull": "🟢", "neutral": "•"}


def _aggregate_by_ticker(items: list) -> dict:
    """Per ticker: {"signal_type": "bear"|"bull"|"neutral", "count": int},
    computed deterministically from the classified items themselves — bear
    beats bull beats neutral, same precedence news_alert.py already uses.
    This is what drives the digest's ranking, not anything Claude reports."""
    agg = {}
    for item in items:
        ticker = item["ticker"]
        entry = agg.setdefault(ticker, {"signal_type": "neutral", "count": 0})
        entry["count"] += 1
        if item["signal_type"] == "bear":
            entry["signal_type"] = "bear"
        elif item["signal_type"] == "bull" and entry["signal_type"] != "bear":
            entry["signal_type"] = "bull"
    return agg


def _format_digest(items: list, result: dict, date_str: str) -> str:
    lines = [f"🤖 <b>AI News Team — Stocks Digest</b> — {date_str}", ""]

    macro = (result.get("macro_overview") or "").strip()
    if macro:
        lines += ["🌍 <b>Macro / Sector</b>", macro, ""]

    agg = _aggregate_by_ticker(items)
    summaries_by_ticker = {s["ticker"]: s.get("summary", "") for s in (result.get("stock_summaries") or [])}

    tickers_sorted = sorted(
        agg.keys(),
        key=lambda t: (_SIGNAL_RANK.get(agg[t]["signal_type"], 3), -agg[t]["count"]),
    )
    for ticker in tickers_sorted:
        summary = summaries_by_ticker.get(ticker, "").strip()
        if not summary:
            continue  # Claude didn't return a summary for this ticker — skip rather than show empty
        emoji = _SIGNAL_EMOJI.get(agg[ticker]["signal_type"], "•")
        lines += [f"{emoji} <b>${ticker}</b>", summary, ""]

    return "\n".join(lines).strip()


def _format_fallback_digest(items: list, date_str: str) -> str:
    """No-Claude fallback: formats classify_ticker_news() items directly —
    the raw matched headline/condition per ticker, grouped and ranked the
    same way the AI digest is — with no natural-language summary text and
    no macro/sector synthesis (there's nothing to synthesize it from
    without a model). Zero API cost. Used when the Claude call fails for
    any reason (no credit, rate limit, network) so the pipeline still
    delivers something instead of nothing."""
    lines = [f"🤖 <b>AI News Team — Stocks Digest (no-AI fallback)</b> — {date_str}", ""]

    agg = _aggregate_by_ticker(items)
    by_ticker: dict = {}
    for item in items:
        by_ticker.setdefault(item["ticker"], []).append(item)

    tickers_sorted = sorted(
        agg.keys(),
        key=lambda t: (_SIGNAL_RANK.get(agg[t]["signal_type"], 3), -agg[t]["count"]),
    )
    for ticker in tickers_sorted:
        emoji = _SIGNAL_EMOJI.get(agg[ticker]["signal_type"], "•")
        lines.append(f"{emoji} <b>${ticker}</b>")
        for item in by_ticker[ticker]:
            lines.append(f"📰 {item['headline']}")
            condition = (item.get("condition") or "").strip()
            if condition:
                lines.append(f"📌 <i>{condition[:120]}</i>")
        lines.append("")

    return "\n".join(lines).strip()


def run(category: dict):
    """Run one category end to end. Missing config (env vars not set yet)
    degrades to a no-op print instead of crashing the workflow step."""
    output_token = os.environ.get(category["output_bot_token_env"])
    output_chat = os.environ.get(category["output_chat_id_env"])
    finnhub_key = os.environ.get(category["finnhub_key_env"])

    if not output_token or not output_chat:
        print(f"run_category[{category['name']}]: output bot token/chat not set, skipping")
        return
    if not finnhub_key:
        print(f"run_category[{category['name']}]: {category['finnhub_key_env']} not set, skipping")
        return

    items = category["collect_items"](finnhub_key, category["max_items"])
    if not items:
        print(f"run_category[{category['name']}]: no matched news today")
        return

    date_str = datetime.now(timezone.utc).strftime("%d %b %Y")
    try:
        result = summarize(items)
        digest = _format_digest(items, result, date_str)
        mode = "AI"
    except Exception as e:
        print(f"run_category[{category['name']}]: Claude summarize failed ({e}), falling back to no-AI digest")
        digest = _format_fallback_digest(items, date_str)
        mode = "fallback"

    send_telegram_chunks(digest, output_token, int(output_chat))
    print(f"run_category[{category['name']}]: sent {mode} digest ({len(items)} matched items)")

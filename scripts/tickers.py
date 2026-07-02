"""Shared ticker lists for news_alert.py and gen_stocks_json.py.

US tickers are derived from briefs/*.md so a new brief is picked up
automatically. TH tickers stay hardcoded (small, needs a .BK symbol
that isn't derivable from the brief filename).
"""
import re
from pathlib import Path

TH_TICKERS = [
    {"ticker": "PTT",   "name": "PTT",                  "symbol": "PTT.BK"},
    {"ticker": "KBANK", "name": "KBank",                "symbol": "KBANK.BK"},
    {"ticker": "AOT",   "name": "Airports of Thailand", "symbol": "AOT.BK"},
]
TH_SET = {s["ticker"] for s in TH_TICKERS}


def _brief_name(path: Path, ticker: str) -> str:
    first_line = path.read_text(encoding="utf-8").splitlines()[0]
    m = re.match(r'^#\s*\S+\s+[—-]\s*(.+)$', first_line)
    return m.group(1).strip() if m else ticker


def us_tickers(briefs_dir: str = "briefs") -> list:
    """[{ticker, name}, ...] for every non-TH ticker that has a brief."""
    out = []
    for path in sorted(Path(briefs_dir).glob("*.md")):
        ticker = path.stem
        if ticker.startswith("_") or ticker in TH_SET:
            continue
        out.append({"ticker": ticker, "name": _brief_name(path, ticker)})
    return out

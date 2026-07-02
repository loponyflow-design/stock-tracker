#!/usr/bin/env python3
"""Regenerate webapp/stocks.json from briefs/*.md — run before every Pages deploy
so the webapp's ticker list never drifts out of sync with briefs/ again."""
import json
from pathlib import Path
from tickers import TH_TICKERS, us_tickers


def main():
    us = us_tickers()
    Path("webapp/stocks.json").write_text(
        json.dumps({"us": us, "th": TH_TICKERS}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"wrote webapp/stocks.json — {len(us)} US, {len(TH_TICKERS)} TH")


if __name__ == "__main__":
    main()

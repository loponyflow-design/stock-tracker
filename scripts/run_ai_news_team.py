#!/usr/bin/env python3
"""Entrypoint: python scripts/run_ai_news_team.py <category>

Only "stocks" (Phase 1) is wired up today. Future categories (world news,
health research, food/business trends) register themselves in
ai_news_team/categories/ and get added to CATEGORIES below.
"""
import sys

from ai_news_team.categories.stocks import CATEGORY as STOCKS_CATEGORY
from ai_news_team.run_category import run

CATEGORIES = {"stocks": STOCKS_CATEGORY}


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "stocks"
    category = CATEGORIES.get(name)
    if not category:
        print(f"Unknown category: {name!r}. Available: {', '.join(CATEGORIES)}")
        sys.exit(1)
    run(category)


if __name__ == "__main__":
    main()

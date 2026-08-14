"""AI news team — modular news pipeline (source -> match -> summarize -> output).

Phase 1 ships a single category, `categories/stocks.py`. Future categories
(world news, health research, food/business trends) are added as new files
under `categories/` that reuse the same `run_category.run()` orchestrator.
"""

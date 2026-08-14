"""Shared Telegram sender — chunked to respect the 4096-char message limit.

Extracted out of scripts/news_alert.py so both the existing bull/bear alert
pipeline and the AI news team pipeline send through the same code instead of
two copies that can drift.
"""
import requests

LIMIT = 3800


def send_telegram_chunks(text: str, bot_token: str, chat_id: int):
    """Send `text` to `chat_id` via `bot_token`, splitting on paragraph
    boundaries (\\n\\n) so each chunk stays under Telegram's 4096-char limit."""
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
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": chunk, "parse_mode": "HTML"},
            timeout=10,
        )
        print(r.text)
        r.raise_for_status()

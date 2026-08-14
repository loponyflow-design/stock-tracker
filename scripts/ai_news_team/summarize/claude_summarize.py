"""Single batched Claude call: turns the day's classified news items
(classify_ticker_news() output — bear/bull/news already known deterministically
from each ticker's brief) into a macro/sector overview plus per-ticker summary
text, in one structured JSON response.

Claude's job is writing the Thai summary text only — signal_type and
importance for ranking the digest are computed downstream from the items
themselves (run_category.py), not re-classified by the model, since we
already trust news_alert.py's own bear/bull matching for that.

One call per run keeps this well under the <$5/month budget, and
claude-haiku-4-5 is the right tier for short-summary work like this.
"""
import json

import anthropic

MODEL = "claude-haiku-4-5"

SYSTEM_PROMPT = (
    "คุณช่วยสรุปข่าวหุ้น/เศรษฐกิจให้นักลงทุนระยะยาว (3 ปีขึ้นไป) ที่สนใจบริษัทพื้นฐานมั่นคง "
    "รายได้สม่ำเสมอ กำไรโต และหลีกเลี่ยงหุ้นที่ผูกกับ macro รุนแรง "
    "สรุปให้กระชับ ตรงประเด็น เน้นข้อเท็จจริงและนัยสำคัญต่อพื้นฐานธุรกิจ ไม่ต้องแนะนำซื้อ/ขาย "
    "สำหรับภาพรวม macro/sector ให้สังเคราะห์จากธีมร่วมที่สังเกตเห็นในข่าวรายหุ้นที่ให้มา "
    "(เช่น ดอกเบี้ย ห่วงโซ่อุปทาน นโยบายภาษี) — ถ้าไม่เห็นธีมร่วมที่ชัดเจนให้ตอบเป็น string ว่าง"
)

SCHEMA = {
    "type": "object",
    "properties": {
        "macro_overview": {
            "type": "string",
            "description": (
                "สรุปภาพรวม macro/sector ที่เกี่ยวข้อง เป็นภาษาไทย 2-4 ประโยค "
                "หรือ string ว่างถ้าไม่มีธีม macro ที่เกี่ยวข้องเลย"
            ),
        },
        "stock_summaries": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string"},
                    "summary": {
                        "type": "string",
                        "description": "สรุปข่าวของหุ้นตัวนี้ 1-3 ประโยค ภาษาไทย",
                    },
                },
                "required": ["ticker", "summary"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["macro_overview", "stock_summaries"],
    "additionalProperties": False,
}


def summarize(items: list) -> dict:
    """`items`: classify_ticker_news() output —
    [{"ticker", "market", "headline", "url", "summary", "ts_label",
      "signal_type": "bear"|"bull"|"news", "condition"}, ...]
    Returns {"macro_overview": str, "stock_summaries": [{"ticker", "summary"}, ...]}
    matching SCHEMA above."""
    client = anthropic.Anthropic()

    lines = []
    for item in items:
        tag = f"[{item['ticker']}/{item['signal_type']}]"
        headline = item["headline"]
        summary = (item.get("summary") or "").strip()
        lines.append(f"- {tag} {headline}" + (f" — {summary}" if summary else ""))
    user_content = "ข่าวที่กรองมาแล้ววันนี้ (ต่อหุ้นที่ถืออยู่):\n" + "\n".join(lines)

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
        messages=[{"role": "user", "content": user_content}],
    )
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)

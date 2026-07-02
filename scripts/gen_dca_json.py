#!/usr/bin/env python3
"""Regenerate webapp/dca.json from the DCA Tracker Apps Script Web App —
run alongside news_alert.py so the dca.html dashboard doesn't drift stale.
Never raises: any failure just leaves the last committed dca.json in place,
so a temporary Apps Script outage can't break the daily news alert step."""
import json
import os
import requests
from pathlib import Path

DCA_WEBAPP_URL = os.environ.get("DCA_WEBAPP_URL")
DCA_WEBAPP_TOKEN = os.environ.get("DCA_WEBAPP_TOKEN")


def main():
    if not DCA_WEBAPP_URL or not DCA_WEBAPP_TOKEN:
        print("gen_dca_json: DCA_WEBAPP_URL/DCA_WEBAPP_TOKEN not set, skipping")
        return

    try:
        resp = requests.get(DCA_WEBAPP_URL, params={"token": DCA_WEBAPP_TOKEN}, timeout=20)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"gen_dca_json: fetch failed, leaving existing dca.json untouched: {e}")
        return

    if data.get("error"):
        # Apps Script Web Apps always answer HTTP 200 — errors are signaled in the body.
        print(f"gen_dca_json: Apps Script returned an error, leaving existing dca.json untouched: {data['error']}")
        return

    Path("webapp/dca.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("wrote webapp/dca.json")


if __name__ == "__main__":
    main()

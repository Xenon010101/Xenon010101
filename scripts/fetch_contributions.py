#!/usr/bin/env python3
"""
Fetch a public GitHub contribution calendar with no token.

GitHub serves the same HTML fragment the profile page itself uses at:
    https://github.com/users/<username>/contributions
Each day is a <td class="ContributionCalendar-day" data-date="..." data-level="...">.
The actual count lives in a separate <tool-tip for="<td-id>"> element
("3 contributions on April 5th." / "No contributions on March 29th.") --
GitHub does not put the count on the cell itself, so both pieces are
scraped and joined by id.
"""
import json
import os
import re
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup

DEFAULT_USERNAME = os.environ.get("GH_USERNAME", "Xenon010101")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")

COUNT_RE = re.compile(r"(No|\d+)\s+contribution")


def fetch_days(username: str) -> list[dict]:
    resp = requests.get(
        f"https://github.com/users/{username}/contributions",
        headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"},
        timeout=20,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    tooltips = {t.get("for"): t.get_text(strip=True) for t in soup.select("tool-tip[for]")}

    days = []
    for cell in soup.select("td.ContributionCalendar-day"):
        d = cell.get("data-date")
        if d is None:
            continue
        level = int(cell.get("data-level", 0) or 0)
        tip = tooltips.get(cell.get("id"), "")
        m = COUNT_RE.match(tip)
        count = 0
        if m:
            count = 0 if m.group(1) == "No" else int(m.group(1))
        days.append({"date": d, "count": count, "level": level})

    days.sort(key=lambda x: x["date"])
    return days


def derive_stats(days: list[dict]) -> dict:
    if not days:
        return {}

    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"])

    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    longest_streak = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    by_month: dict[str, int] = {}
    for d in days:
        key = d["date"][:7]
        by_month[key] = by_month.get(key, 0) + d["count"]

    return {
        "total": total,
        "best_day": {"date": best["date"], "count": best["count"]},
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "by_month": by_month,
    }


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_USERNAME
    days = fetch_days(username)
    payload = {
        "username": username,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "days": days,
        "stats": derive_stats(days),
    }
    out_path = os.path.abspath(OUT_PATH)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote {len(days)} days ({payload['stats'].get('total', 0)} total contributions) -> {out_path}")


if __name__ == "__main__":
    main()

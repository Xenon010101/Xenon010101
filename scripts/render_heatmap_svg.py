#!/usr/bin/env python3
"""
Render data/contributions.json as an animated SVG contribution heatmap.

Boxes slide/fade in on a diagonal (week + day offset), staggered, then
freeze -- no infinite looping. Pure CSS keyframes inside the SVG, so it
plays on GitHub with zero JS.
"""
import json
import os
from collections import defaultdict
from datetime import datetime

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "contrib-heatmap.svg")

# level -> fill color (dark terminal background, phosphor-green ramp)
PALETTE = ["#0d1117", "#0e4429", "#006d32", "#26a641", "#39d353"]

CELL = 11
GAP = 3
LEFT_PAD = 28
TOP_PAD = 20
MONTH_LABEL_H = 16


def month_abbr(m: int) -> str:
    return [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ][m - 1]


def build_weeks(days: list[dict]) -> list[list[dict | None]]:
    """Bucket days into GitHub-style weeks (columns of 7, Sun-Sat)."""
    by_date = {d["date"]: d for d in days}
    dates = sorted(by_date)
    if not dates:
        return []

    start = datetime.strptime(dates[0], "%Y-%m-%d")
    end = datetime.strptime(dates[-1], "%Y-%m-%d")

    # back up to the preceding Sunday so week columns align
    start_sunday = start
    while start_sunday.weekday() != 6:  # Python Mon=0..Sun=6
        from datetime import timedelta
        start_sunday -= timedelta(days=1)

    from datetime import timedelta

    weeks: list[list[dict | None]] = []
    cur = start_sunday
    week: list[dict | None] = []
    while cur <= end:
        key = cur.strftime("%Y-%m-%d")
        week.append(by_date.get(key))
        if len(week) == 7:
            weeks.append(week)
            week = []
        cur += timedelta(days=1)
    if week:
        while len(week) < 7:
            week.append(None)
        weeks.append(week)
    return weeks


def render(payload: dict) -> str:
    days = payload["days"]
    stats = payload.get("stats", {})
    weeks = build_weeks(days)
    n_weeks = len(weeks)

    width = LEFT_PAD + n_weeks * (CELL + GAP) + 40
    grid_h = 7 * (CELL + GAP)
    height = TOP_PAD + MONTH_LABEL_H + grid_h + 46  # + legend/footer

    rects = []
    max_delay = 0.0
    last_month = None
    month_labels = []

    for wi, week in enumerate(weeks):
        for di, day in enumerate(week):
            x = LEFT_PAD + wi * (CELL + GAP)
            y = TOP_PAD + MONTH_LABEL_H + di * (CELL + GAP)
            if day is None:
                continue
            level = min(day["level"], 4)
            color = PALETTE[level]
            dt = datetime.strptime(day["date"], "%Y-%m-%d")
            if dt.day <= 7 and dt.month != last_month:
                last_month = dt.month
                month_labels.append((x, month_abbr(dt.month)))

            delay = (wi + di) * 0.012
            max_delay = max(max_delay, delay)
            title = f"{day['count']} contributions on {day['date']}"
            rects.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" ry="2.5" '
                f'fill="{color}" class="cell" style="animation-delay:{delay:.3f}s">'
                f"<title>{title}</title></rect>"
            )

    month_label_svg = "".join(
        f'<text x="{x}" y="{TOP_PAD + MONTH_LABEL_H - 4}" class="month">{label}</text>'
        for x, label in month_labels
    )

    legend_x = LEFT_PAD
    legend_y = TOP_PAD + MONTH_LABEL_H + grid_h + 20
    legend_swatches = "".join(
        f'<rect x="{legend_x + 34 + i * (CELL + GAP)}" y="{legend_y - 9}" '
        f'width="{CELL}" height="{CELL}" rx="2.5" fill="{PALETTE[i]}"/>'
        for i in range(5)
    )

    total = stats.get("total", 0)
    streak = stats.get("current_streak", 0)
    longest = stats.get("longest_streak", 0)
    footer = (
        f'<text x="{LEFT_PAD}" y="{legend_y + 20}" class="footer">'
        f"{total} contributions in the last year &#183; current streak {streak}d &#183; longest {longest}d</text>"
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="'SF Mono','Fira Code',Consolas,monospace">
  <style>
    .month {{ fill: #7d8590; font-size: 10px; }}
    .legend-label {{ fill: #7d8590; font-size: 10px; }}
    .footer {{ fill: #c9d1d9; font-size: 11px; }}
    .cell {{
      opacity: 0;
      transform-box: fill-box;
      transform-origin: center;
      transform: scale(0.4) translate(-6px, -6px);
      animation: reveal 0.5s ease-out forwards;
    }}
    @keyframes reveal {{
      to {{ opacity: 1; transform: scale(1) translate(0, 0); }}
    }}
  </style>
  <rect width="100%" height="100%" fill="#0d1117" rx="6"/>
  {month_label_svg}
  {"".join(rects)}
  <text x="{legend_x}" y="{legend_y}" class="legend-label">Less</text>
  {legend_swatches}
  <text x="{legend_x + 34 + 5 * (CELL + GAP) + 6}" y="{legend_y}" class="legend-label">More</text>
  {footer}
</svg>'''


def main():
    with open(os.path.abspath(DATA_PATH)) as f:
        payload = json.load(f)
    svg = render(payload)
    out_path = os.path.abspath(OUT_PATH)
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Hand-authored neofetch-style info card as an SVG.
Lines fade + slide in on a stagger, then freeze (no infinite loop).
Edit the CONTENT block below -- this is copy, not scraped data.
"""
import os

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")

WIDTH = 490
LINE_H = 22
PAD_X = 20
TITLE_H = 34

# ---- content -------------------------------------------------------
TITLE = "xenon@github"
ROWS = [
    ("Role", "Full-Stack Developer (JS/TS + Python)"),
    ("Base", "Kolkata, IN"),
    ("Now", "GSSoC 2026 contributor"),
    ("Stack", "React * Node * Express * Firebase * Docker"),
    ("Building", "SwastSevak (AI for health workers)"),
    ("Shipped", "InsiderEdge * PresentAI"),
]
# ---------------------------------------------------------------------

KEY_COLOR = "#39d353"
VAL_COLOR = "#c9d1d9"
BG = "#0d1117"
BORDER = "#30363d"
DOT_COLORS = ["#ff5f56", "#ffbd2e", "#27c93f"]


def render() -> str:
    height = TITLE_H + len(ROWS) * LINE_H + 24
    key_col_w = max(len(k) for k, _ in ROWS) * 8 + 16

    rows_svg = []
    for i, (key, val) in enumerate(ROWS):
        y = TITLE_H + 26 + i * LINE_H
        delay = 0.15 + i * 0.09
        rows_svg.append(
            f'<g class="line" style="animation-delay:{delay:.2f}s">'
            f'<text x="{PAD_X}" y="{y}" fill="{KEY_COLOR}" font-weight="600">{key}</text>'
            f'<text x="{PAD_X + key_col_w}" y="{y}" fill="{VAL_COLOR}">{val}</text>'
            f"</g>"
        )

    dots = "".join(
        f'<circle cx="{20 + i * 16}" cy="{TITLE_H / 2}" r="5" fill="{c}"/>'
        for i, c in enumerate(DOT_COLORS)
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" font-family="'SF Mono','Fira Code',Consolas,monospace" font-size="13">
  <style>
    .line {{
      opacity: 0;
      transform: translateX(-8px);
      animation: fadein 0.4s ease-out forwards;
    }}
    @keyframes fadein {{
      to {{ opacity: 1; transform: translateX(0); }}
    }}
  </style>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="8" fill="{BG}" stroke="{BORDER}"/>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{TITLE_H}" rx="8" fill="#161b22"/>
  <rect x="0.5" y="{TITLE_H - 8}" width="{WIDTH - 1}" height="8" fill="#161b22"/>
  {dots}
  <text x="{WIDTH / 2}" y="{TITLE_H / 2 + 4}" fill="#7d8590" font-size="11" text-anchor="middle">{TITLE}</text>
  <line x1="0" y1="{TITLE_H}" x2="{WIDTH}" y2="{TITLE_H}" stroke="{BORDER}"/>
  {"".join(rows_svg)}
</svg>'''


def main():
    svg = render()
    out_path = os.path.abspath(OUT_PATH)
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()

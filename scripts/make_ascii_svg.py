#!/usr/bin/env python3
"""
Convert a prepped (background-removed, contrast-boosted, white-composited)
grayscale photo into a monochrome ASCII-art SVG that "types" itself in
row by row, then freezes.

Design choices (deliberate, not defaults):
  - One light-gray fill color -- per-character rainbow coloring is what
    makes most ASCII portraits look like TV static.
  - High local contrast + white background -> only the subject prints;
    the background maps to the blank end of the ramp (space).
  - Reveal is a left-to-right clip-path wipe per row, staggered top to
    bottom, done once (no looping).
"""
import os
import sys

from PIL import Image

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense); leading space clears bg

COLS = 100
CHAR_W = 7
CHAR_H = 13
FONT_SIZE = 12
ASPECT_CORRECTION = 0.46  # monospace chars are taller than wide

FILL = "#c9d1d9"
BG = "#0d1117"

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "avi-ascii.svg")


def image_to_grid(path: str, cols: int) -> list[str]:
    img = Image.open(path).convert("L")
    w, h = img.size
    rows = max(1, round(cols * (h / w) * ASPECT_CORRECTION))
    small = img.resize((cols, rows), Image.LANCZOS)

    ramp_len = len(RAMP)
    lines = []
    for y in range(rows):
        chars = []
        for x in range(cols):
            brightness = small.getpixel((x, y))  # 0=black .. 255=white
            idx = int((255 - brightness) / 255 * (ramp_len - 1))
            chars.append(RAMP[idx])
        lines.append("".join(chars))
    return lines


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render(lines: list[str]) -> str:
    n_rows = len(lines)
    grid_w = COLS * CHAR_W
    grid_h = n_rows * CHAR_H
    pad = 16
    width = grid_w + pad * 2
    height = grid_h + pad * 2

    clip_defs = []
    groups = []
    for i, line in enumerate(lines):
        y = pad + i * CHAR_H
        baseline = y + CHAR_H - 3
        delay = i * 0.018
        clip_defs.append(
            f'<clipPath id="rc{i}">'
            f'<rect x="{pad}" y="{y}" width="0" height="{CHAR_H}" '
            f'class="wiperect" style="animation-delay:{delay:.3f}s"/>'
            f"</clipPath>"
        )
        groups.append(
            f'<g clip-path="url(#rc{i})">'
            f'<text x="{pad}" y="{baseline}" xml:space="preserve" class="ascii-line">'
            f"{esc(line)}</text></g>"
        )

    total_delay = n_rows * 0.018 + 0.4
    cursor_x = pad
    cursor_y = pad + n_rows * CHAR_H + 4

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="'SF Mono','Fira Code',Consolas,monospace" font-size="{FONT_SIZE}">
  <defs>
    {"".join(clip_defs)}
  </defs>
  <style>
    .ascii-line {{ fill: {FILL}; white-space: pre; letter-spacing: 0; }}
    .wiperect {{ animation: wipein 0.32s linear forwards; }}
    @keyframes wipein {{ to {{ width: {grid_w}px; }} }}
    .cursor {{
      opacity: 0;
      animation: blink 0.5s steps(1) 3, fadeout 0.01s linear forwards;
      animation-delay: {total_delay:.2f}s, {total_delay + 1.5:.2f}s;
    }}
    @keyframes blink {{ 50% {{ opacity: 1; }} }}
    @keyframes fadeout {{ to {{ opacity: 0; }} }}
  </style>
  <rect width="100%" height="100%" fill="{BG}"/>
  {"".join(groups)}
  <rect x="{cursor_x}" y="{cursor_y}" width="{CHAR_W - 1}" height="{CHAR_H - 3}" fill="{FILL}" class="cursor"/>
</svg>'''


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "source-photo-prepped.png"
    lines = image_to_grid(src, COLS)
    svg = render(lines)
    out_path = os.path.abspath(OUT_PATH)
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"Wrote {out_path} ({COLS}x{len(lines)} grid)")


if __name__ == "__main__":
    main()

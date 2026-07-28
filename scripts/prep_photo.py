#!/usr/bin/env python3
"""
Prep a source photo for ASCII conversion.

A flatly-lit face converts to a dark, unreadable blob, so:
  1. Remove the background with rembg (isolate the subject).
  2. Boost local contrast with CLAHE -- gives a flat face real
     highlights/shadows.
  3. Composite onto pure white so the background maps to the blank
     end of the ASCII ramp (white -> space).
Output: a grayscale <name>-prepped.png next to the source.
"""
import sys
import os

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep(source_path: str) -> str:
    with open(source_path, "rb") as f:
        input_bytes = f.read()

    # 1. remove background -> RGBA with subject isolated
    out_bytes = remove(input_bytes)
    rgba = Image.open(__import__("io").BytesIO(out_bytes)).convert("RGBA")

    # 1b. crop to the subject's bounding box (+ small padding) so we don't
    # spend character rows on empty background above/around the subject
    alpha = np.array(rgba)[:, :, 3]
    ys, xs = np.where(alpha > 20)
    if len(xs):
        pad = int(0.02 * max(rgba.size))
        left = max(0, xs.min() - pad)
        right = min(rgba.width, xs.max() + pad)
        top = max(0, ys.min() - pad)
        bottom = min(rgba.height, ys.max() + pad)
        rgba = rgba.crop((left, top, right, bottom))

    # 1c. bust-level crop: keep head/shoulders/upper chest, drop the rest
    # of the torso so the portrait reads as an avatar, not a full body shot
    bust_fraction = float(os.environ.get("BUST_FRACTION", "0.56"))
    rgba = rgba.crop((0, 0, rgba.width, int(rgba.height * bust_fraction)))

    # 2. composite onto pure white using the alpha mask
    white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, rgba).convert("RGB")

    # 3. CLAHE contrast boost (convert to grayscale first)
    gray = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # re-flatten near-white background that CLAHE may have darkened slightly
    # (anything above 235 pre-CLAHE was background; force it back to white)
    orig_gray = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2GRAY)
    bg_mask = orig_gray > 240
    enhanced[bg_mask] = 255

    out_path = os.path.splitext(source_path)[0] + "-prepped.png"
    Image.fromarray(enhanced).save(out_path)
    return out_path


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg"
    result = prep(src)
    print(f"Wrote {result}")

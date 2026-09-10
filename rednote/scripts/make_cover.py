#!/usr/bin/env python3
"""Generate Rednote video covers for Sudoku Dojo technique lessons.

Layout (accepted C version, no logo on publish frames):
  - 1296×2304, square corners
  - white Heiti + blue stroke on deep navy grid background
  - cover: title + tier line at half size (default 数独初级技巧)
  - ending: title + formula lines at equal size

Requires: pip install pillow
Fonts: STHeiti Medium (macOS), else Noto Sans CJK Bold/Regular (Linux)

Examples:
  python3 make_cover.py cover 显性唯一
  python3 make_cover.py cover 显性数对 --tier 数独中级技巧
  python3 make_cover.py ending 排除法 --lines 选数字 划行列 看宫里剩哪
  python3 make_cover.py ending 隐性唯一 \\
      --lines 数字只剩一落点 必须填 显性唯一看格子 隐性唯一看数字
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
COVERS = HERE.parent / "video" / "covers"
ASSETS = COVERS / "_assets"
BG = ASSETS / "background.png"

W, H = 1296, 2304
BG_SCALE = 1.75
BG_FOCUS_Y = 0.52

# Prefer macOS STHeiti; fall back to Noto Sans CJK on Linux.
_TITLE_FONT_CANDIDATES = (
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
)
TITLE_SIZE_COVER = 210
TITLE_SIZE_ENDING = 150
TITLE_Y_COVER = 620
TITLE_Y_ENDING = 520
TITLE_STROKE_COVER = 10
TITLE_STROKE_ENDING = 8

SUB_SIZE = TITLE_SIZE_COVER // 2
SUB_Y = 940
SUB_STROKE = 5
DEFAULT_TIER = "数独初级技巧"

FORMULA_SIZE = 84
FORMULA_STROKE = 4
FORMULA_START_Y = 860
FORMULA_GAP = 200

FILL = (255, 255, 255, 255)
STROKE_FILL = (59, 130, 246, 255)


def resolve_title_font() -> str:
    for path in _TITLE_FONT_CANDIDATES:
        if Path(path).is_file():
            return path
    raise SystemExit(
        "no CJK title font found; tried:\n  " + "\n  ".join(_TITLE_FONT_CANDIDATES)
    )


TITLE_FONT = resolve_title_font()


def load_background() -> Image.Image:
    if not BG.is_file():
        raise SystemExit(f"missing background: {BG}")
    src = Image.open(BG).convert("RGBA")
    base = src.resize((W, H), Image.Resampling.LANCZOS)
    cw, ch = int(W / BG_SCALE), int(H / BG_SCALE)
    cx, cy = W // 2, int(H * BG_FOCUS_Y)
    left = max(0, min(W - cw, cx - cw // 2))
    top = max(0, min(H - ch, cy - ch // 2))
    return base.crop((left, top, left + cw, top + ch)).resize(
        (W, H), Image.Resampling.LANCZOS
    )


def center_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    y: int,
    stroke: int,
) -> None:
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
    tw = bbox[2] - bbox[0]
    tx = (W - tw) / 2 - bbox[0]
    ty = y - bbox[1]
    draw.text(
        (tx, ty),
        text,
        font=font,
        fill=FILL,
        stroke_width=stroke,
        stroke_fill=STROKE_FILL,
    )


def render_cover(title: str, tier: str = DEFAULT_TIER) -> Image.Image:
    canvas = load_background()
    draw = ImageDraw.Draw(canvas)
    title_font = ImageFont.truetype(TITLE_FONT, TITLE_SIZE_COVER, index=0)
    center_text(draw, title, title_font, TITLE_Y_COVER, TITLE_STROKE_COVER)
    if tier.strip():
        sub_font = ImageFont.truetype(TITLE_FONT, SUB_SIZE, index=0)
        center_text(draw, tier.strip(), sub_font, SUB_Y, SUB_STROKE)
    return canvas.convert("RGB")


def render_ending(title: str, lines: list[str]) -> Image.Image:
    canvas = load_background()
    draw = ImageDraw.Draw(canvas)
    title_font = ImageFont.truetype(TITLE_FONT, TITLE_SIZE_ENDING, index=0)
    center_text(draw, title, title_font, TITLE_Y_ENDING, TITLE_STROKE_ENDING)
    formula_font = ImageFont.truetype(TITLE_FONT, FORMULA_SIZE, index=0)
    y = FORMULA_START_Y
    for line in lines:
        line = line.strip()
        if not line:
            continue
        center_text(draw, line, formula_font, y, FORMULA_STROKE)
        y += FORMULA_GAP
    return canvas.convert("RGB")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sudoku Dojo Rednote cover generator")
    sub = parser.add_subparsers(dest="mode", required=True)

    cover = sub.add_parser("cover", help="Title + tier line")
    cover.add_argument("title", help="Chinese technique name, e.g. 唯一余数")
    cover.add_argument(
        "--tier",
        default=DEFAULT_TIER,
        help=f'Tier line (default: "{DEFAULT_TIER}"). Empty string to omit.',
    )
    cover.add_argument("-o", "--output", type=Path, help="PNG path")

    ending = sub.add_parser("ending", help="Title + formula lines")
    ending.add_argument("title", help="Chinese technique name")
    ending.add_argument(
        "--lines",
        nargs="+",
        required=True,
        help="Formula lines, same font size each",
    )
    ending.add_argument("-o", "--output", type=Path, help="PNG path")

    args = parser.parse_args()
    title = args.title.strip()
    if not title:
        raise SystemExit("title is empty")

    COVERS.mkdir(parents=True, exist_ok=True)

    if args.mode == "cover":
        out = args.output or (COVERS / f"{title}.png")
        render_cover(title, args.tier).save(out, "PNG")
    else:
        out = args.output or (COVERS / f"{title}-结尾.png")
        render_ending(title, args.lines).save(out, "PNG")

    print(out)


if __name__ == "__main__":
    main()

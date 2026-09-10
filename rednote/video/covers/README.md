# Rednote video covers

Portrait frames (1296×2304) for technique videos. No logo, square corners.

## Assets

- `_assets/background.png` — navy grid background (do not overwrite casually)
- `_assets/logo.png` — app icon, kept for optional branded variants

## Generate

From `sudocool-operations/rednote/scripts`:

```bash
# cover: title + 数独初级技巧
python3 make_cover.py cover 唯一余数

# cover with another tier
python3 make_cover.py cover 显性数对 --tier 数独中级技巧

# ending: title + formula lines (same size)
python3 make_cover.py ending 排除法 --lines 选数字 划行列 看宫里剩哪
```

Needs Pillow (`pip install pillow`) and macOS STHeiti.

Outputs land in this folder as `<标题>.png` / `<标题>-结尾.png`.

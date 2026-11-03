# exporter.py
import io
import pathlib
from datetime import date
from PIL import Image, ImageDraw, ImageFont


DISCLAIMER_LINES = [
    "Wondr Diamonds Pvt. Ltd.",
    "IT Infrastructure Team",
    "For authorized store staff only.",
]

_LOGO_PATH = pathlib.Path(__file__).parent / "assets" / "LOGO.png"

# ── Colour palette (matches app.py THEME) ─────────────────────────────
GOLD = "#AA832B"
GOLD_LIGHT = "#C9A84C"
WHITE = "#FFFFFF"
TEXT_DARK = "#2B2B2B"
BG_LIGHT = "#FFF8EE"
CARD_BG = "#FFFFFF"
FIELD_BG = "#F5F0E8"          # disabled-input tint from app.py
URL_COLOR = "#1A5276"         # dark-blue for URLs
GOLD_BORDER_RGB = (170, 131, 43)
GOLD_LIGHT_RGB = (201, 168, 76)


# ── Font helpers ──────────────────────────────────────────────────────
def _load_font(paths: list[str], size: int) -> ImageFont.FreeTypeFont:
    """Try each TTF path; fall back to Pillow default."""
    for p in paths:
        try:
            return ImageFont.truetype(p, size=size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default(size=size)


def _bold(size: int) -> ImageFont.FreeTypeFont:
    return _load_font([
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/calibrib.ttf",
        "C:/Windows/Fonts/verdanab.ttf",
    ], size)


def _regular(size: int) -> ImageFont.FreeTypeFont:
    return _load_font([
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/verdana.ttf",
    ], size)


# ── Rounded-rect helper ──────────────────────────────────────────────
def _rounded_rect(draw: ImageDraw.ImageDraw, xy, radius, fill=None, outline=None, width=1):
    """Draw a rectangle with rounded corners."""
    x0, y0, x1, y1 = xy
    r = radius
    # Four corner circles
    draw.ellipse([x0, y0, x0 + 2 * r, y0 + 2 * r], fill=fill, outline=outline, width=width)
    draw.ellipse([x1 - 2 * r, y0, x1, y0 + 2 * r], fill=fill, outline=outline, width=width)
    draw.ellipse([x0, y1 - 2 * r, x0 + 2 * r, y1], fill=fill, outline=outline, width=width)
    draw.ellipse([x1 - 2 * r, y1 - 2 * r, x1, y1], fill=fill, outline=outline, width=width)
    # Rectangles that fill the middle
    draw.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
    draw.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)
    # Outline edges (if needed)
    if outline and width:
        draw.arc([x0, y0, x0 + 2 * r, y0 + 2 * r], 180, 270, fill=outline, width=width)
        draw.arc([x1 - 2 * r, y0, x1, y0 + 2 * r], 270, 0, fill=outline, width=width)
        draw.arc([x0, y1 - 2 * r, x0 + 2 * r, y1], 90, 180, fill=outline, width=width)
        draw.arc([x1 - 2 * r, y1 - 2 * r, x1, y1], 0, 90, fill=outline, width=width)
        draw.line([x0 + r, y0, x1 - r, y0], fill=outline, width=width)
        draw.line([x0 + r, y1, x1 - r, y1], fill=outline, width=width)
        draw.line([x0, y0 + r, x0, y1 - r], fill=outline, width=width)
        draw.line([x1, y0 + r, x1, y1 - r], fill=outline, width=width)


# ── Gradient band helper ─────────────────────────────────────────────
def _gradient_band(img: Image.Image, x0, y0, x1, y1, left_rgb, right_rgb):
    """Draw a horizontal linear gradient from left_rgb → right_rgb."""
    w = x1 - x0
    if w <= 0:
        return
    for i in range(w):
        ratio = i / w
        r = int(left_rgb[0] + (right_rgb[0] - left_rgb[0]) * ratio)
        g = int(left_rgb[1] + (right_rgb[1] - left_rgb[1]) * ratio)
        b = int(left_rgb[2] + (right_rgb[2] - left_rgb[2]) * ratio)
        draw = ImageDraw.Draw(img)
        draw.line([(x0 + i, y0), (x0 + i, y1)], fill=(r, g, b))


def build_credential_grid(
    zone: str,
    branch: str,
    credentials: list,
    fmt: str,
    export_date: str | None = None,
):
    """
    Renders a polished credential sheet matching the app.py theme:
      • Gold gradient header with logo + bold branch name
      • 3×5 card grid with rounded corners, gradient title strips,
        tinted field rows, and clearly visible URLs
      • Gold gradient footer with disclaimer
    Returns (bytes, mime_type, extension).
    """
    if export_date is None:
        export_date = date.today().strftime("%d %b %Y").upper()

    # ── Fonts ─────────────────────────────────────────────────────────
    f_branch = _bold(42)
    f_subtitle = _regular(17)
    f_date = _bold(15)
    f_card_title = _bold(17)
    f_card_sub = _regular(13)
    f_label = _bold(13)
    f_value = _regular(14)
    f_url_value = _bold(13)
    f_footer = _regular(13)
    f_footer_bold = _bold(14)

    # ── Layout dimensions ─────────────────────────────────────────────
    header_h = 120
    footer_h = 70
    canvas_w = 1800
    cols, rows = 3, 5
    margin_x, margin_top = 32, 14
    gap_x, gap_y = 20, 16
    card_w = (canvas_w - 2 * margin_x - (cols - 1) * gap_x) // cols
    card_h = 290
    grid_h = rows * card_h + (rows - 1) * gap_y + 2 * margin_top
    canvas_h = header_h + grid_h + footer_h

    img = Image.new("RGB", (canvas_w, canvas_h), color=BG_LIGHT)
    draw = ImageDraw.Draw(img)

    # ── Header gradient band ──────────────────────────────────────────
    _gradient_band(img, 0, 0, canvas_w, header_h, GOLD_BORDER_RGB, GOLD_LIGHT_RGB)
    draw = ImageDraw.Draw(img)  # refresh after gradient

    # Logo (top-left, on white pad with rounded feel)
    logo_img = Image.open(_LOGO_PATH).convert("RGBA")
    logo_h = header_h - 20
    aspect = logo_img.width / logo_img.height
    logo_w = int(logo_h * aspect)
    logo_img = logo_img.resize((logo_w, logo_h), Image.LANCZOS)
    logo_bg = Image.new("RGBA", (logo_w + 12, logo_h + 8), (255, 255, 255, 230))
    logo_bg.paste(logo_img, (6, 4), logo_img)
    img.paste(logo_bg.convert("RGB"), (14, 10))

    # Branch name (bold, large, white)
    text_x = 14 + logo_w + 12 + 24
    draw.text((text_x, 20), branch.upper(), fill=WHITE, font=f_branch)

    # Subtitle
    branch_bb = draw.textbbox((0, 0), branch.upper(), font=f_branch)
    branch_text_h = branch_bb[3] - branch_bb[1]
    draw.text(
        (text_x, 20 + branch_text_h + 6),
        "IT INFRASTRUCTURE & SYSTEM ACCESS GUIDE",
        fill=WHITE,
        font=f_subtitle,
    )

    # Date (top-right)
    date_text = f"AS ON {export_date}"
    date_bb = draw.textbbox((0, 0), date_text, font=f_date)
    date_tw = date_bb[2] - date_bb[0]
    draw.text(
        (canvas_w - date_tw - 36, 24),
        date_text,
        fill=WHITE,
        font=f_date,
    )

    # ── 3 × 5 Card Grid ──────────────────────────────────────────────
    grid_top = header_h + margin_top

    for idx, item in enumerate(credentials):
        r = idx // cols
        c = idx % cols
        x0 = margin_x + c * (card_w + gap_x)
        y0 = grid_top + r * (card_h + gap_y)
        x1 = x0 + card_w
        y1 = y0 + card_h
        corner_r = 10

        # ── Card background (white, rounded, gold border) ─────────
        _rounded_rect(draw, (x0, y0, x1, y1), corner_r, fill=CARD_BG, outline=GOLD, width=2)

        # ── Card title strip (gradient, top rounded corners) ──────
        subtitle = item.get("subtitle", "")
        strip_h = 42 if not subtitle else 56

        # Gradient title strip
        _gradient_band(img, x0 + 1, y0 + 1, x1 - 1, y0 + strip_h, GOLD_BORDER_RGB, GOLD_LIGHT_RGB)
        draw = ImageDraw.Draw(img)

        # Title text
        title_text = f"{idx + 1}. {item['title']}"
        draw.text((x0 + 14, y0 + 10), title_text, fill=WHITE, font=f_card_title)
        if subtitle:
            draw.text(
                (x0 + 30, y0 + 32),
                subtitle,
                fill=WHITE,
                font=f_card_sub,
            )

        # ── Thin gold divider below title strip ───────────────────
        draw.line([(x0 + 1, y0 + strip_h), (x1 - 1, y0 + strip_h)], fill=GOLD, width=1)

        # ── Data rows: constants then editable fields ─────────────
        data_rows = []
        for const in item.get("constants", []):
            data_rows.append((const["label"], const["value"], True))
        for field in item.get("fields", []):
            val = field.get("value", "") or "____________________"
            data_rows.append((field["label"], val, False))

        fy = y0 + strip_h + 6
        row_h = 40
        row_inner_pad = 8
        val_x = x0 + 14

        for ri, (rlabel, rval, is_const) in enumerate(data_rows):
            row_y0 = fy
            row_y1 = fy + row_h - 2

            # Alternating row background for readability
            if ri % 2 == 0:
                draw.rectangle(
                    [(x0 + 2, row_y0), (x1 - 2, row_y1)],
                    fill=FIELD_BG,
                )

            # Label (gold, bold)
            draw.text((val_x, row_y0 + 2), f"{rlabel}:", fill=GOLD, font=f_label)

            # Value
            if is_const:
                val_text = str(rval)[:52]
                draw.text(
                    (val_x, row_y0 + 18),
                    val_text,
                    fill=URL_COLOR,
                    font=f_url_value,
                )
            else:
                draw.text(
                    (val_x, row_y0 + 18),
                    str(rval)[:52],
                    fill=TEXT_DARK,
                    font=f_value,
                )

            fy += row_h

    # ── Footer gradient band ──────────────────────────────────────────
    footer_y = canvas_h - footer_h
    _gradient_band(img, 0, footer_y, canvas_w, canvas_h, GOLD_BORDER_RGB, GOLD_LIGHT_RGB)
    draw = ImageDraw.Draw(img)

    # Footer text (centered)
    line_h = 20
    total_text_h = len(DISCLAIMER_LINES) * line_h
    start_y = footer_y + (footer_h - total_text_h) // 2
    for i, line in enumerate(DISCLAIMER_LINES):
        font = f_footer_bold if i == 0 else f_footer
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(
            ((canvas_w - tw) // 2, start_y + i * line_h),
            line,
            fill=WHITE,
            font=font,
        )

    # ── Encode ────────────────────────────────────────────────────────
    buf = io.BytesIO()
    if fmt == "JPEG":
        img.save(buf, format="JPEG", quality=95)
        return buf.getvalue(), "image/jpeg", "jpg"

    img.save(buf, format="PDF", resolution=150.0)
    return buf.getvalue(), "application/pdf", "pdf"

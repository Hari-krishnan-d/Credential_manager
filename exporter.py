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


def build_credential_grid(
    zone: str,
    branch: str,
    credentials: list,
    fmt: str,
    export_date: str | None = None,
):
    """
    Renders the credential sheet with:
      • Logo (top-left)
      • Branch name in BOLD  +  subtitle line
      • Date (top-right)
      • 3×5 card grid with variable fields per card
      • Disclaimer footer
    Returns (bytes, mime_type, extension).
    """
    if export_date is None:
        export_date = date.today().strftime("%d %b %Y").upper()

    # ── Layout dimensions ─────────────────────────────────────────────
    header_h = 130
    footer_h = 64
    canvas_w = 1800
    grid_h = 1540
    canvas_h = header_h + grid_h + footer_h

    gold = "#AA832B"
    white = "#FFFFFF"
    text_dark = "#2B2B2B"
    bg_light = "#FFF8EE"

    img = Image.new("RGB", (canvas_w, canvas_h), color=bg_light)
    draw = ImageDraw.Draw(img)

    # ── Fonts ─────────────────────────────────────────────────────────
    branch_font = ImageFont.load_default(size=30)
    subtitle_font = ImageFont.load_default(size=18)
    date_font = ImageFont.load_default(size=16)
    card_header_font = ImageFont.load_default(size=18)
    label_font = ImageFont.load_default(size=14)
    value_font = ImageFont.load_default(size=15)
    footer_font = ImageFont.load_default(size=13)

    # ── Header band ──────────────────────────────────────────────────
    draw.rectangle([(0, 0), (canvas_w, header_h)], fill=gold)

    # Logo (top-left)
    logo_img = Image.open(_LOGO_PATH).convert("RGBA")
    logo_h = header_h - 16
    aspect = logo_img.width / logo_img.height
    logo_w = int(logo_h * aspect)
    logo_img = logo_img.resize((logo_w, logo_h), Image.LANCZOS)
    # White background pad behind logo for clean look
    logo_bg = Image.new("RGBA", (logo_w, logo_h), (255, 255, 255, 255))
    logo_bg.paste(logo_img, (0, 0), logo_img)
    img.paste(logo_bg, (16, 8))

    # Text right of logo
    text_x = 16 + logo_w + 20

    # Branch name (BOLD / large)
    draw.text((text_x, 18), branch.upper(), fill=white, font=branch_font)

    # Subtitle
    draw.text(
        (text_x, 56),
        "IT INFRASTRUCTURE & SYSTEM ACCESS GUIDE",
        fill=white,
        font=subtitle_font,
    )

    # Zone (smaller)
    draw.text((text_x, 84), f"Zone: {zone}", fill=white, font=label_font)

    # Date (top-right)
    date_text = f"AS ON {export_date}"
    bbox = draw.textbbox((0, 0), date_text, font=date_font)
    date_tw = bbox[2] - bbox[0]
    draw.text(
        (canvas_w - date_tw - 30, 20),
        date_text,
        fill=white,
        font=date_font,
    )

    # ── 3 × 5 Card Grid ──────────────────────────────────────────────
    cols, rows = 3, 5
    margin_x = 36
    margin_y = header_h + 16
    gap_x, gap_y = 24, 18
    card_w = (canvas_w - 2 * margin_x - (cols - 1) * gap_x) // cols
    card_h = (grid_h - 32 - (rows - 1) * gap_y) // rows

    for idx, item in enumerate(credentials):
        r = idx // cols
        c = idx % cols
        x0 = margin_x + c * (card_w + gap_x)
        y0 = margin_y + r * (card_h + gap_y)
        x1 = x0 + card_w
        y1 = y0 + card_h

        # Card body (white, gold border)
        draw.rectangle([(x0, y0), (x1, y1)], fill=white, outline=gold, width=2)

        # Card header strip
        strip_h = 40
        subtitle = item.get("subtitle", "")
        if subtitle:
            strip_h = 54
        draw.rectangle([(x0, y0), (x1, y0 + strip_h)], fill=gold)

        # Title text
        title_text = f"{idx + 1}. {item['title']}"
        draw.text((x0 + 12, y0 + 8), title_text, fill=white, font=card_header_font)
        if subtitle:
            draw.text(
                (x0 + 28, y0 + 30),
                subtitle,
                fill=white,
                font=label_font,
            )

        # ── Build rows: constants first, then editable fields ─────
        data_rows = []
        for const in item.get("constants", []):
            data_rows.append((const["label"], const["value"]))
        for field in item.get("fields", []):
            val = field.get("value", "") or "____________________"
            data_rows.append((field["label"], val))

        fy = y0 + strip_h + 8
        row_h = 36
        for rlabel, rval in data_rows:
            draw.text((x0 + 12, fy), f"{rlabel}:", fill=gold, font=label_font)
            draw.text((x0 + 12, fy + 16), str(rval)[:52], fill=text_dark, font=value_font)
            fy += row_h

    # ── Disclaimer Footer ─────────────────────────────────────────────
    footer_y = canvas_h - footer_h
    draw.rectangle([(0, footer_y), (canvas_w, canvas_h)], fill=gold)

    line_h = 18
    total_text_h = len(DISCLAIMER_LINES) * line_h
    start_y = footer_y + (footer_h - total_text_h) // 2
    for i, line in enumerate(DISCLAIMER_LINES):
        bbox = draw.textbbox((0, 0), line, font=footer_font)
        tw = bbox[2] - bbox[0]
        draw.text(
            ((canvas_w - tw) // 2, start_y + i * line_h),
            line,
            fill=white,
            font=footer_font,
        )

    # ── Encode ────────────────────────────────────────────────────────
    buf = io.BytesIO()
    if fmt == "JPEG":
        img.save(buf, format="JPEG", quality=95)
        return buf.getvalue(), "image/jpeg", "jpg"

    img.save(buf, format="PDF", resolution=150.0)
    return buf.getvalue(), "application/pdf", "pdf"
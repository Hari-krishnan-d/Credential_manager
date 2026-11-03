# exporter.py
import io
import pathlib
from datetime import date
from PIL import Image, ImageDraw, ImageFont


DISCLAIMER = "Wondr Diamonds Pvt. Ltd.  ·  IT Infrastructure Team  ·  For authorized store staff only"

_LOGO_PATH = pathlib.Path(__file__).parent / "assets" / "LOGO.png"

# ── Colour palette (matches app.py / reference poster) ────────────────
GOLD = "#AA832B"
GOLD_RGB = (170, 131, 43)
GOLD_LIGHT = "#C9A84C"
WHITE = "#FFFFFF"
TEXT_DARK = "#2B2B2B"
BG_CREAM = "#F5F0E8"
CARD_BG = "#FFFFFF"
BORDER_GOLD = "#AA832B"
DARK_BOX = "#2B2B2B"


# ── Font helpers ──────────────────────────────────────────────────────
def _load(paths: list[str], size: int):
    for p in paths:
        try:
            return ImageFont.truetype(p, size=size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default(size=size)


def _bold(sz):
    return _load(["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/calibrib.ttf"], sz)


def _regular(sz):
    return _load(["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/calibri.ttf"], sz)


def _italic(sz):
    return _load(["C:/Windows/Fonts/ariali.ttf", "C:/Windows/Fonts/calibrii.ttf"], sz)


# ── Rounded-rect helper ──────────────────────────────────────────────
def _rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    x0, y0, x1, y1 = xy
    r = min(radius, (x1 - x0) // 2, (y1 - y0) // 2)
    # Filled body
    if fill:
        draw.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
        draw.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)
        draw.pieslice([x0, y0, x0 + 2 * r, y0 + 2 * r], 180, 270, fill=fill)
        draw.pieslice([x1 - 2 * r, y0, x1, y0 + 2 * r], 270, 360, fill=fill)
        draw.pieslice([x0, y1 - 2 * r, x0 + 2 * r, y1], 90, 180, fill=fill)
        draw.pieslice([x1 - 2 * r, y1 - 2 * r, x1, y1], 0, 90, fill=fill)
    # Outline
    if outline:
        draw.arc([x0, y0, x0 + 2 * r, y0 + 2 * r], 180, 270, fill=outline, width=width)
        draw.arc([x1 - 2 * r, y0, x1, y0 + 2 * r], 270, 360, fill=outline, width=width)
        draw.arc([x0, y1 - 2 * r, x0 + 2 * r, y1], 90, 180, fill=outline, width=width)
        draw.arc([x1 - 2 * r, y1 - 2 * r, x1, y1], 0, 90, fill=outline, width=width)
        draw.line([x0 + r, y0, x1 - r, y0], fill=outline, width=width)
        draw.line([x0 + r, y1, x1 - r, y1], fill=outline, width=width)
        draw.line([x0, y0 + r, x0, y1 - r], fill=outline, width=width)
        draw.line([x1, y0 + r, x1, y1 - r], fill=outline, width=width)


def build_credential_grid(
    zone: str,
    branch: str,
    credentials: list,
    fmt: str,
    export_date: str | None = None,
):
    """
    Renders a credential sheet matching the reference poster design:
      • Cream background, clean header with logo + bold branch name
      • Date in a bordered box (top-right)
      • 3×5 card grid — circle icon, bold title, thin gold divider,
        label LEFT / value RIGHT on same row
      • Single-line footer
    Returns (bytes, mime_type, extension).
    """
    if export_date is None:
        export_date = date.today().strftime("%d %b %Y").upper()

    # ── Fonts ─────────────────────────────────────────────────────────
    f_branch = _bold(52)
    f_guide = _bold(18)
    f_date = _bold(16)
    f_card_title = _bold(20)
    f_card_sub = _italic(14)
    f_label = _bold(14)
    f_value = _regular(14)
    f_footer = _regular(13)

    # ── Layout ────────────────────────────────────────────────────────
    canvas_w = 1800
    header_h = 140
    footer_h = 60
    cols, rows = 3, 5
    margin_x = 40
    margin_top = 20
    gap_x, gap_y = 24, 22
    card_w = (canvas_w - 2 * margin_x - (cols - 1) * gap_x) // cols
    card_h = 280
    grid_h = rows * card_h + (rows - 1) * gap_y + 2 * margin_top
    canvas_h = header_h + grid_h + footer_h

    img = Image.new("RGB", (canvas_w, canvas_h), color=BG_CREAM)
    draw = ImageDraw.Draw(img)

    # ═══════════════════════════════════════════════════════════════════
    #  HEADER — cream background, logo left, branch bold, date boxed
    # ═══════════════════════════════════════════════════════════════════

    # Logo (white background pad — original style)
    logo_img = Image.open(_LOGO_PATH).convert("RGBA")
    logo_h = header_h - 20
    aspect = logo_img.width / logo_img.height
    logo_w = int(logo_h * aspect)
    logo_img = logo_img.resize((logo_w, logo_h), Image.LANCZOS)
    logo_bg = Image.new("RGBA", (logo_w, logo_h), (255, 255, 255, 255))
    logo_bg.paste(logo_img, (0, 0), logo_img)
    logo_x = margin_x
    logo_y = (header_h - logo_h) // 2
    img.paste(logo_bg.convert("RGB"), (logo_x, logo_y))

    # Branch name — large bold, dark text
    text_x = logo_x + logo_w + 24
    branch_text = branch.upper()
    branch_bb = draw.textbbox((0, 0), branch_text, font=f_branch)
    branch_text_h = branch_bb[3] - branch_bb[1]
    branch_y = logo_y
    draw.text((text_x, branch_y), branch_text, fill=TEXT_DARK, font=f_branch)

    # Subtitle line — gold, well below branch name (extra spacing)
    guide_text = "IT INFRASTRUCTURE & SYSTEM ACCESS GUIDE"
    guide_y = branch_y + branch_text_h + 22
    draw.text((text_x, guide_y), guide_text, fill=GOLD, font=f_guide)

    # Date box — top-right, bordered rectangle
    date_text = f"AS ON {export_date}"
    date_bb = draw.textbbox((0, 0), date_text, font=f_date)
    date_tw = date_bb[2] - date_bb[0]
    date_th = date_bb[3] - date_bb[1]
    date_pad_x, date_pad_y = 20, 10
    date_box_w = date_tw + 2 * date_pad_x
    date_box_h = date_th + 2 * date_pad_y
    date_box_x = canvas_w - margin_x - date_box_w
    date_box_y = (header_h - date_box_h) // 2
    _rounded_rect(draw,
                  (date_box_x, date_box_y, date_box_x + date_box_w, date_box_y + date_box_h),
                  radius=6, fill=BG_CREAM, outline=TEXT_DARK, width=2)
    draw.text(
        (date_box_x + date_pad_x, date_box_y + date_pad_y),
        date_text, fill=TEXT_DARK, font=f_date,
    )

    # ═══════════════════════════════════════════════════════════════════
    #  CARD GRID — 3 × 5
    # ═══════════════════════════════════════════════════════════════════
    grid_top = header_h + margin_top

    for idx, item in enumerate(credentials):
        r = idx // cols
        c = idx % cols
        x0 = margin_x + c * (card_w + gap_x)
        y0 = grid_top + r * (card_h + gap_y)
        x1 = x0 + card_w
        y1 = y0 + card_h
        corner_r = 14

        # Card background — white, thin gold border, rounded
        _rounded_rect(draw, (x0, y0, x1, y1), corner_r,
                       fill=CARD_BG, outline=GOLD, width=2)

        # ── Card header: circle icon + bold title ─────────────────
        circle_r = 14
        circle_cx = x0 + 24 + circle_r
        title_baseline_y = y0 + 20
        circle_cy = title_baseline_y + 10
        draw.ellipse(
            [circle_cx - circle_r, circle_cy - circle_r,
             circle_cx + circle_r, circle_cy + circle_r],
            outline=GOLD, width=2,
        )

        title_x = circle_cx + circle_r + 12
        title_text = f"{item['title']}"
        draw.text((title_x, title_baseline_y), title_text, fill=TEXT_DARK, font=f_card_title)

        subtitle = item.get("subtitle", "")
        title_bb = draw.textbbox((0, 0), title_text, font=f_card_title)
        title_text_h = title_bb[3] - title_bb[1]

        divider_y = title_baseline_y + title_text_h + 8
        if subtitle:
            draw.text((title_x, title_baseline_y + title_text_h + 4),
                       subtitle, fill=GOLD, font=f_card_sub)
            divider_y = title_baseline_y + title_text_h + 4 + 18 + 6

        # Thin gold divider line
        draw.line([(x0 + 16, divider_y), (x1 - 16, divider_y)], fill=GOLD, width=1)

        # ── Data rows: LABEL (left)   VALUE (right-aligned) ───────
        data_rows = []
        for const in item.get("constants", []):
            data_rows.append((const["label"], const["value"]))
        for field in item.get("fields", []):
            val = field.get("value", "") or "____________________"
            data_rows.append((field["label"], val))

        fy = divider_y + 10
        row_h = 28
        label_x = x0 + 20
        value_right_x = x1 - 20

        for rlabel, rval in data_rows:
            # Label — bold, left-aligned
            draw.text((label_x, fy), rlabel, fill=TEXT_DARK, font=f_label)

            # Value — regular, right-aligned
            val_text = str(rval)[:48]
            val_bb = draw.textbbox((0, 0), val_text, font=f_value)
            val_tw = val_bb[2] - val_bb[0]
            draw.text((value_right_x - val_tw, fy), val_text, fill=TEXT_DARK, font=f_value)

            fy += row_h

    # ═══════════════════════════════════════════════════════════════════
    #  FOOTER — single centred line on cream background
    # ═══════════════════════════════════════════════════════════════════
    footer_y = canvas_h - footer_h
    footer_bb = draw.textbbox((0, 0), DISCLAIMER, font=f_footer)
    footer_tw = footer_bb[2] - footer_bb[0]
    draw.text(
        ((canvas_w - footer_tw) // 2, footer_y + (footer_h - (footer_bb[3] - footer_bb[1])) // 2),
        DISCLAIMER, fill=TEXT_DARK, font=f_footer,
    )

    # ── Encode ────────────────────────────────────────────────────────
    buf = io.BytesIO()
    if fmt == "JPEG":
        img.save(buf, format="JPEG", quality=95)
        return buf.getvalue(), "image/jpeg", "jpg"

    img.save(buf, format="PDF", resolution=150.0)
    return buf.getvalue(), "application/pdf", "pdf"

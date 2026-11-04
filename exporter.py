# exporter.py
import io
import pathlib
from datetime import date
from PIL import Image, ImageDraw, ImageFont


DISCLAIMER = "Wondr Diamonds Pvt. Ltd.  ·  IT Infrastructure Team  ·  For authorized store staff only"

_LOGO_PATH = pathlib.Path(__file__).parent / "assets" / "LOGO.png"

# ── Colour palette (matches app.py / reference poster) ────────────────
GOLD       = "#AA832B"
GOLD_RGB   = (170, 131, 43)
GOLD_LIGHT = "#C9A84C"
WHITE      = "#FFFFFF"
TEXT_DARK  = "#2B2B2B"
BG_CREAM   = "#F5F0E8"
CARD_BG    = "#FFFFFF"
BORDER_GOLD = "#AA832B"
DARK_BOX   = "#2B2B2B"


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
    if fill:
        draw.rectangle([x0 + r, y0, x1 - r, y1], fill=fill)
        draw.rectangle([x0, y0 + r, x1, y1 - r], fill=fill)
        draw.pieslice([x0, y0, x0 + 2 * r, y0 + 2 * r], 180, 270, fill=fill)
        draw.pieslice([x1 - 2 * r, y0, x1, y0 + 2 * r], 270, 360, fill=fill)
        draw.pieslice([x0, y1 - 2 * r, x0 + 2 * r, y1], 90, 180, fill=fill)
        draw.pieslice([x1 - 2 * r, y1 - 2 * r, x1, y1], 0, 90, fill=fill)
    if outline:
        draw.arc([x0, y0, x0 + 2 * r, y0 + 2 * r], 180, 270, fill=outline, width=width)
        draw.arc([x1 - 2 * r, y0, x1, y0 + 2 * r], 270, 360, fill=outline, width=width)
        draw.arc([x0, y1 - 2 * r, x0 + 2 * r, y1], 90, 180, fill=outline, width=width)
        draw.arc([x1 - 2 * r, y1 - 2 * r, x1, y1], 0, 90, fill=outline, width=width)
        draw.line([x0 + r, y0, x1 - r, y0], fill=outline, width=width)
        draw.line([x0 + r, y1, x1 - r, y1], fill=outline, width=width)
        draw.line([x0, y0 + r, x0, y1 - r], fill=outline, width=width)
        draw.line([x1, y0 + r, x1, y1 - r], fill=outline, width=width)


# ── Icon map: title keyword → Unicode emoji/symbol ───────────────────
_ICON_MAP = [
    ("sso",        "\U0001F511"),   # 🔑  key
    ("cloud erp",  "\u2601"),       # ☁   cloud
    ("erp",        "\U0001F5A5"),   # 🖥   desktop
    ("rfid",       "\U0001F4E1"),   # 📡  satellite
    ("tiara",      "\U0001F48E"),   # 💎  gem
    ("zithara",    "\U0001F91D"),   # 🤝  handshake
    ("outlook",    "\U0001F4E7"),   # 📧  email
    ("mail",       "\U0001F4E7"),   # 📧  email
    ("biometric",  "\U0001F446"),   # 👆  finger
    ("staff wifi", "\U0001F4F6"),   # 📶  wifi
    ("guest wifi", "\U0001F4F6"),   # 📶  wifi
    ("wifi",       "\U0001F4F6"),   # 📶  wifi
    ("chit",       "\U0001F4CB"),   # 📋  clipboard
    ("gift",       "\U0001F381"),   # 🎁  gift
    ("estimation", "\U0001F4CA"),   # 📊  chart
    ("website",    "\U0001F310"),   # 🌐  globe
    ("chat",       "\U0001F4AC"),   # 💬  speech bubble
]


def _pick_icon(title: str) -> str:
    t = title.lower()
    for key, sym in _ICON_MAP:
        if key in t:
            return sym
    return "\U0001F512"   # 🔒 generic fallback


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
      • 3×5 card grid — gold header band with icon badge + bold white title,
        italic subtitle, gold divider, alternating-tint data rows,
        label LEFT / value RIGHT
      • Gold-ruled footer disclaimer
    Returns (bytes, mime_type, extension).
    """
    if export_date is None:
        export_date = date.today().strftime("%d %b %Y").upper()

    # ── Fonts ─────────────────────────────────────────────────────────
    f_branch     = _bold(58)        # Header: branch name
    f_guide      = _bold(24)        # Header: subtitle tagline
    f_date       = _bold(22)        # Header: date box
    f_card_title = _bold(28)        # Card: title on gold band
    f_card_sub   = _italic(20)      # Card: subtitle below band
    f_label      = _bold(20)        # Row: credential label (left)
    f_value      = _regular(20)     # Row: credential value (right)
    f_footer     = _regular(18)     # Footer disclaimer

    # Segoe UI Emoji for crisp Unicode glyphs on Windows
    f_icon = _load(
        ["C:/Windows/Fonts/seguiemj.ttf",
         "C:/Windows/Fonts/seguisym.ttf",
         "C:/Windows/Fonts/arial.ttf"],
        30,
    )

    # ── Layout constants ──────────────────────────────────────────────
    canvas_w   = 2100
    header_h   = 165
    footer_h   = 72
    cols, rows = 3, 5
    margin_x   = 50
    margin_top = 30
    gap_x, gap_y = 32, 30
    card_w = (canvas_w - 2 * margin_x - (cols - 1) * gap_x) // cols
    card_h = 350            # taller cards for comfortable breathing room
    grid_h = rows * card_h + (rows - 1) * gap_y + 2 * margin_top
    canvas_h = header_h + grid_h + footer_h

    img  = Image.new("RGB", (canvas_w, canvas_h), color=BG_CREAM)
    draw = ImageDraw.Draw(img)

    # ═══════════════════════════════════════════════════════════════════
    #  HEADER
    # ═══════════════════════════════════════════════════════════════════

    # Logo
    logo_img = Image.open(_LOGO_PATH).convert("RGBA")
    logo_h   = header_h - 24
    logo_w   = int(logo_h * (logo_img.width / logo_img.height))
    logo_img = logo_img.resize((logo_w, logo_h), Image.LANCZOS)
    logo_bg  = Image.new("RGBA", (logo_w, logo_h), (255, 255, 255, 255))
    logo_bg.paste(logo_img, (0, 0), logo_img)
    logo_x   = margin_x
    logo_y   = (header_h - logo_h) // 2
    img.paste(logo_bg.convert("RGB"), (logo_x, logo_y))

    # Branch + guide subtitle — vertically centred as a block
    text_x        = logo_x + logo_w + 32
    branch_text   = branch.upper()
    branch_bb     = draw.textbbox((0, 0), branch_text, font=f_branch)
    branch_text_h = branch_bb[3] - branch_bb[1]
    guide_text    = "IT INFRASTRUCTURE & SYSTEM ACCESS GUIDE"
    guide_bb      = draw.textbbox((0, 0), guide_text, font=f_guide)
    guide_text_h  = guide_bb[3] - guide_bb[1]
    block_h       = branch_text_h + 12 + guide_text_h
    block_y       = (header_h - block_h) // 2
    draw.text((text_x, block_y),                       branch_text, fill=TEXT_DARK, font=f_branch)
    draw.text((text_x, block_y + branch_text_h + 12),  guide_text,  fill=GOLD,      font=f_guide)

    # Date box — top-right corner
    date_text    = f"AS ON  {export_date}"
    date_bb      = draw.textbbox((0, 0), date_text, font=f_date)
    date_tw      = date_bb[2] - date_bb[0]
    date_th      = date_bb[3] - date_bb[1]
    date_pad_x, date_pad_y = 24, 14
    date_box_w   = date_tw + 2 * date_pad_x
    date_box_h   = date_th + 2 * date_pad_y
    date_box_x   = canvas_w - margin_x - date_box_w
    date_box_y   = (header_h - date_box_h) // 2
    _rounded_rect(draw,
                  (date_box_x, date_box_y,
                   date_box_x + date_box_w, date_box_y + date_box_h),
                  radius=10, fill=BG_CREAM, outline=GOLD, width=3)
    draw.text(
        (date_box_x + date_pad_x, date_box_y + date_pad_y),
        date_text, fill=TEXT_DARK, font=f_date,
    )

    # Gold rule under header
    draw.line([(0, header_h - 3), (canvas_w, header_h - 3)], fill=GOLD, width=4)

    # ═══════════════════════════════════════════════════════════════════
    #  CARD GRID — 3 × 5
    # ═══════════════════════════════════════════════════════════════════
    grid_top      = header_h + margin_top
    header_band_h = 58       # gold strip at top of each card
    corner_r      = 16

    for idx, item in enumerate(credentials):
        r  = idx // cols
        c  = idx % cols
        x0 = margin_x + c * (card_w + gap_x)
        y0 = grid_top + r * (card_h + gap_y)
        x1 = x0 + card_w
        y1 = y0 + card_h

        # Soft drop shadow
        sh = 5
        _rounded_rect(draw, (x0 + sh, y0 + sh, x1 + sh, y1 + sh),
                       corner_r, fill="#D4C9B0")

        # Card body — white, gold border
        _rounded_rect(draw, (x0, y0, x1, y1), corner_r,
                       fill=CARD_BG, outline=GOLD, width=3)

        # Gold header band — paint rounded-top rect, then mask lower overlap
        _rounded_rect(draw,
                       (x0, y0, x1, y0 + header_band_h + corner_r),
                       corner_r, fill=GOLD)
        draw.rectangle(
            [x0 + 1, y0 + header_band_h, x1 - 1, y0 + header_band_h + corner_r + 2],
            fill=CARD_BG,
        )

        # Icon badge — white rounded square on the gold band
        badge_sz = 44
        badge_x  = x0 + 16
        badge_y  = y0 + (header_band_h - badge_sz) // 2
        _rounded_rect(draw,
                       (badge_x, badge_y,
                        badge_x + badge_sz, badge_y + badge_sz),
                       radius=10, fill=WHITE, outline=GOLD_LIGHT, width=1)

        icon_char   = _pick_icon(item["title"])
        icon_bb     = draw.textbbox((0, 0), icon_char, font=f_icon)
        icon_draw_x = badge_x + (badge_sz - (icon_bb[2] - icon_bb[0])) // 2 - icon_bb[0]
        icon_draw_y = badge_y + (badge_sz - (icon_bb[3] - icon_bb[1])) // 2 - icon_bb[1]
        draw.text((icon_draw_x, icon_draw_y), icon_char, fill=TEXT_DARK, font=f_icon)

        # Card title — bold white text on gold band
        title_text = item["title"]
        title_x    = badge_x + badge_sz + 14
        title_bb   = draw.textbbox((0, 0), title_text, font=f_card_title)
        title_h    = title_bb[3] - title_bb[1]
        title_y    = y0 + (header_band_h - title_h) // 2
        draw.text((title_x, title_y), title_text, fill=WHITE, font=f_card_title)

        # Subtitle — italic gold, below the gold band
        content_y = y0 + header_band_h + 12
        subtitle   = item.get("subtitle", "")
        if subtitle:
            draw.text((x0 + 20, content_y), subtitle, fill=GOLD, font=f_card_sub)
            content_y += 30

        # Thin gold divider
        draw.line([(x0 + 16, content_y), (x1 - 16, content_y)], fill=GOLD, width=2)
        content_y += 14

        # Data rows — LABEL (left, bold gold)   VALUE (right, dark)
        data_rows = []
        for const in item.get("constants", []):
            data_rows.append((const["label"], const["value"]))
        for field in item.get("fields", []):
            val = field.get("value", "") or "____________________"
            data_rows.append((field["label"], val))

        row_h         = 38
        label_x       = x0 + 20
        value_right_x = x1 - 20

        for ri, (rlabel, rval) in enumerate(data_rows):
            # Alternating row tint
            if ri % 2 == 0:
                tint_y0 = content_y - 4
                tint_y1 = content_y + row_h - 6
                draw.rectangle([x0 + 4, tint_y0, x1 - 4, tint_y1],
                                fill="#FAF6EE")

            # Label — bold, gold colour, left-aligned
            draw.text((label_x, content_y), rlabel, fill=GOLD_RGB, font=f_label)

            # Value — regular, dark, right-aligned, truncated to 52 chars
            val_text = str(rval)[:52]
            val_bb   = draw.textbbox((0, 0), val_text, font=f_value)
            val_tw   = val_bb[2] - val_bb[0]
            draw.text((value_right_x - val_tw, content_y), val_text,
                       fill=TEXT_DARK, font=f_value)

            content_y += row_h

    # ═══════════════════════════════════════════════════════════════════
    #  FOOTER — gold rule + centred disclaimer
    # ═══════════════════════════════════════════════════════════════════
    footer_top = canvas_h - footer_h
    draw.line([(0, footer_top), (canvas_w, footer_top)], fill=GOLD, width=3)

    footer_bb = draw.textbbox((0, 0), DISCLAIMER, font=f_footer)
    footer_tw = footer_bb[2] - footer_bb[0]
    footer_th = footer_bb[3] - footer_bb[1]
    draw.text(
        ((canvas_w - footer_tw) // 2,
         footer_top + (footer_h - footer_th) // 2),
        DISCLAIMER, fill=TEXT_DARK, font=f_footer,
    )

    # ── Encode ────────────────────────────────────────────────────────
    buf = io.BytesIO()
    if fmt == "JPEG":
        img.save(buf, format="JPEG", quality=95)
        return buf.getvalue(), "image/jpeg", "jpg"

    img.save(buf, format="PDF", resolution=150.0)
    return buf.getvalue(), "application/pdf", "pdf"

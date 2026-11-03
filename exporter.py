# exporter.py
import io
from PIL import Image, ImageDraw, ImageFont


def build_credential_grid(zone: str, branch: str, credentials: list, fmt: str):
    """
    Statelessly renders all 15 credential cards in a 3x5 grid in RAM.
    Returns (bytes_data, mime_type, file_extension).
    """
    canvas_w, canvas_h = 1800, 1520
    bg_dark = "#080E05"
    gold = "#AA832B"
    white = "#FFFFFF"

    img = Image.new("RGB", (canvas_w, canvas_h), color=bg_dark)
    draw = ImageDraw.Draw(img)

    title_font = ImageFont.load_default(size=32)
    header_font = ImageFont.load_default(size=20)
    label_font = ImageFont.load_default(size=15)
    value_font = ImageFont.load_default(size=16)

    # Top Master Banner
    draw.rectangle([(0, 0), (canvas_w, 100)], fill=gold)
    draw.text((40, 32), "COMPANY CREDENTIAL MASTER SHEET", fill=bg_dark, font=title_font)
    branch_tag = f"ZONE: {zone.upper()}   |   BRANCH: {branch.upper()}"
    draw.text((canvas_w - 650, 38), branch_tag, fill=bg_dark, font=header_font)

    # 3 Columns x 5 Rows Grid Layout
    cols, rows = 3, 5
    margin_x, margin_y = 40, 130
    gap_x, gap_y = 30, 25
    card_w = (canvas_w - (2 * margin_x) - ((cols - 1) * gap_x)) // cols
    card_h = (canvas_h - margin_y - 40 - ((rows - 1) * gap_y)) // rows

    for idx, item in enumerate(credentials):
        r = idx // cols
        c = idx % cols
        x0 = margin_x + c * (card_w + gap_x)
        y0 = margin_y + r * (card_h + gap_y)
        x1 = x0 + card_w
        y1 = y0 + card_h

        # Card White Body with Gold Border
        draw.rectangle([(x0, y0), (x1, y1)], fill=white, outline=gold, width=3)

        # Card Header Strip (#AA832B)
        draw.rectangle([(x0, y0), (x1, y0 + 48)], fill=gold)
        draw.text((x0 + 16, y0 + 13), f"{idx + 1}. {item['title']}", fill=bg_dark, font=header_font)

        # Card Fields (Constant Identifier, Username, Password)
        fields = [
            (f"{item['id_label']} (Constant)", item["id_value"]),
            ("Username", item["username"] or "-"),
            ("Password", item["password"] or "-"),
        ]

        fy = y0 + 62
        for flabel, fval in fields:
            draw.text((x0 + 16, fy), f"{flabel}:", fill=gold, font=label_font)
            draw.text((x0 + 16, fy + 20), str(fval)[:48], fill=bg_dark, font=value_font)
            draw.line([(x0 + 16, fy + 48), (x1 - 16, fy + 48)], fill="#E2E8F0", width=1)
            fy += 58

    buf = io.BytesIO()
    if fmt == "JPEG":
        img.save(buf, format="JPEG", quality=95)
        return buf.getvalue(), "image/jpeg", "jpg"

    img.save(buf, format="PDF", resolution=150.0)
    return buf.getvalue(), "application/pdf", "pdf"
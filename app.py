# app.py
import streamlit as st
from datetime import date
from config import APPLICATIONS, THEME, ALL_BRANCHES, BRANCH_TO_ZONE
from exporter import build_credential_grid
import pathlib

st.set_page_config(page_title="Wondr Diamonds – IT Infrastructure Guide", layout="wide")

# ── Paths & dates ─────────────────────────────────────────────────────
_logo_path = pathlib.Path(__file__).parent / "assets" / "LOGO.png"
today_str = date.today().strftime("%d %b %Y").upper()   # e.g. "03 NOV 2026"

# ── Custom CSS – Gold & White light theme ─────────────────────────────
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {THEME['bg']};
            color: {THEME['text']};
        }}

        /* ── Credential cards ── */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border: 2px solid {THEME['gold']} !important;
            border-radius: 10px !important;
            background-color: {THEME['card']} !important;
        }}
        .card-title {{
            background: linear-gradient(135deg, {THEME['gold']}, {THEME['gold_light']});
            color: {THEME['white']};
            padding: 8px 14px;
            border-radius: 6px;
            font-weight: 700;
            margin-bottom: 8px;
            line-height: 1.3;
        }}
        .card-title .card-subtitle {{
            font-size: 12px;
            font-weight: 500;
            opacity: 0.9;
        }}

        /* ── Input field styling ── */
        input[type="text"], input[type="password"] {{
            background-color: {THEME['white']} !important;
            color: {THEME['text']} !important;
            border: 1.5px solid {THEME['gold']}66 !important;
            border-radius: 6px !important;
        }}
        input[type="text"]:focus, input[type="password"]:focus {{
            border-color: {THEME['gold']} !important;
            box-shadow: 0 0 0 2px {THEME['gold']}33 !important;
        }}

        /* ── Selectbox / radio tweaks ── */
        div[data-baseweb="select"] {{
            background-color: {THEME['white']} !important;
            border-radius: 6px !important;
        }}
        label {{
            color: {THEME['text']} !important;
        }}

        /* ── Download button ── */
        button[data-testid="stDownloadButton"] {{
            background: linear-gradient(135deg, {THEME['gold']}, {THEME['gold_light']}) !important;
            color: {THEME['white']} !important;
            font-weight: 700 !important;
            border: none !important;
            border-radius: 8px !important;
        }}

        /* ── Divider colour ── */
        hr {{
            border-color: {THEME['gold']}44 !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header: Logo (left) + Date (right) ───────────────────────────────
header_left, header_right = st.columns([5, 1.5])
with header_left:
    st.image(str(_logo_path), width=140)
with header_right:
    st.markdown(
        f"""
        <div style="text-align:right; padding-top:24px;
                    font-weight:700; font-size:15px; color:{THEME['gold']};">
            AS ON {today_str}
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    f"""
    <p style="font-size:18px; font-weight:600; color:{THEME['gold']};
              margin-top:-8px; margin-bottom:0;">
        IT Infrastructure and System Access Guide
    </p>
    """,
    unsafe_allow_html=True,
)
st.divider()

# ── Branch & Format selection ─────────────────────────────────────────
sel_c1, sel_c2 = st.columns([3, 2])
with sel_c1:
    selected_branch = st.selectbox("Select Branch", ALL_BRANCHES)
with sel_c2:
    export_format = st.radio("Download Format", ["PDF", "JPEG"], horizontal=True)

selected_zone = BRANCH_TO_ZONE[selected_branch]

st.divider()

# ── Auto-apply callback ──────────────────────────────────────────────
def _trigger_rerun():
    pass  # on_change presence forces Streamlit to rerun on blur/tab

# ── 3-Column Grid for the 15 Applications ─────────────────────────────
collected_credentials = []
grid_cols = st.columns(3)

for idx, app in enumerate(APPLICATIONS):
    col = grid_cols[idx % 3]
    with col:
        with st.container(border=True):
            # ── Card header ───────────────────────────────────────
            subtitle_html = ""
            if app.get("subtitle"):
                subtitle_html = f'<div class="card-subtitle">{app["subtitle"]}</div>'
            st.markdown(
                f'<div class="card-title">{idx + 1}. {app["title"]}{subtitle_html}</div>',
                unsafe_allow_html=True,
            )

            # ── Constant fields (read-only) ───────────────────────
            for ci, const in enumerate(app.get("constants", [])):
                st.text_input(
                    const["label"],
                    value=const["value"],
                    disabled=True,
                    key=f"const_{idx}_{ci}",
                )

            # ── Editable fields ───────────────────────────────────
            field_values = []
            for fi, field in enumerate(app.get("fields", [])):
                is_pw = field["type"] == "password"
                val = st.text_input(
                    field["label"],
                    key=f"field_{idx}_{fi}",
                    type="password" if is_pw else "default",
                    placeholder="____________________",
                    on_change=_trigger_rerun,
                )
                field_values.append({"label": field["label"], "value": val.strip()})

            collected_credentials.append(
                {
                    "title": app["title"],
                    "subtitle": app.get("subtitle", ""),
                    "constants": app.get("constants", []),
                    "fields": field_values,
                }
            )

st.divider()

# ── Validation & Download ─────────────────────────────────────────────
apps_with_fields = [c for c in collected_credentials if c["fields"]]
all_filled = all(all(f["value"] for f in c["fields"]) for c in apps_with_fields)
any_filled = any(any(f["value"] for f in c["fields"]) for c in apps_with_fields)

btn_col1, btn_col2 = st.columns([2, 1])
with btn_col1:
    allow_partial = st.checkbox(
        "Allow download even if some cards are left blank", value=False
    )

can_download = all_filled or (allow_partial and any_filled)

if can_download:
    file_bytes, mime_type, ext = build_credential_grid(
        zone=selected_zone,
        branch=selected_branch,
        credentials=collected_credentials,
        fmt=export_format,
        export_date=today_str,
    )
    st.download_button(
        label=f"Download {selected_branch} Credentials as {export_format}",
        data=file_bytes,
        file_name=f"Credentials_{selected_branch}.{ext}".replace(" ", "_"),
        mime=mime_type,
        type="primary",
        use_container_width=True,
    )
else:
    st.warning(
        "Fill in all editable fields (or check 'Allow download even if some cards are blank') "
        "to unlock the download button."
    )
# app.py
import streamlit as st
from config import APPLICATIONS, THEME, ZONES_AND_BRANCHES
from exporter import build_credential_grid
import base64, pathlib

st.set_page_config(page_title="Wondr Diamonds – Branch Credential Grid", layout="wide")

# ── Load logo as base64 for inline embedding ──────────────────────────
_logo_path = pathlib.Path(__file__).parent / "assets" / "LOGO.png"
_logo_b64 = base64.b64encode(_logo_path.read_bytes()).decode()

# ── Custom CSS – refreshed colour palette ─────────────────────────────
# Primary dark  → #0F1724 (deep navy, much more contrast vs. old #080E05)
# Card surface  → #1A2332 (subtle lift off the background)
# Gold accent   → kept #AA832B
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {THEME['dark']};
            color: {THEME['white']};
        }}

        /* ── Top banner with right-aligned logo ── */
        .top-banner {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: linear-gradient(135deg, {THEME['gold']}, #C9A84C);
            color: {THEME['dark']};
            padding: 12px 24px;
            border-radius: 10px;
            font-weight: 800;
            font-size: 22px;
            margin-bottom: 20px;
            box-shadow: 0 4px 14px rgba(170,131,43,.45);
        }}
        .top-banner img {{
            height: 54px;
            border-radius: 6px;
        }}

        /* ── Credential cards ── */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border: 2px solid {THEME['gold']} !important;
            border-radius: 10px !important;
            background-color: {THEME['card']} !important;
        }}
        .card-title {{
            background: linear-gradient(135deg, {THEME['gold']}, #C9A84C);
            color: {THEME['dark']};
            padding: 6px 14px;
            border-radius: 6px;
            font-weight: 700;
            margin-bottom: 10px;
        }}

        /* ── Input field styling ── */
        input[type="text"], input[type="password"] {{
            background-color: {THEME['card']} !important;
            color: {THEME['white']} !important;
            border: 1px solid {THEME['gold']}44 !important;
            border-radius: 6px !important;
        }}
        input[type="text"]:focus, input[type="password"]:focus {{
            border-color: {THEME['gold']} !important;
            box-shadow: 0 0 0 2px {THEME['gold']}33 !important;
        }}

        /* ── Selectbox / radio tweaks ── */
        div[data-baseweb="select"] {{
            background-color: {THEME['card']} !important;
            border-radius: 6px !important;
        }}
        label {{
            color: {THEME['white']} !important;
        }}

        /* ── Download button ── */
        button[data-testid="stDownloadButton"] {{
            background: linear-gradient(135deg, {THEME['gold']}, #C9A84C) !important;
            color: {THEME['dark']} !important;
            font-weight: 700 !important;
            border: none !important;
            border-radius: 8px !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Top Banner with logo on the RIGHT ─────────────────────────────────
st.markdown(
    f"""
    <div class="top-banner">
        <span>WONDR DIAMONDS – CREDENTIAL MASTER GRID</span>
        <img src="data:image/png;base64,{_logo_b64}" alt="Wondr Diamonds Logo" />
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Top Bar: Zone, Branch & Output Format Selection ───────────────────
top_c1, top_c2, top_c3 = st.columns([2, 2, 2])
with top_c1:
    selected_zone = st.selectbox("Select Zone", list(ZONES_AND_BRANCHES.keys()))
with top_c2:
    selected_branch = st.selectbox("Select Branch", ZONES_AND_BRANCHES[selected_zone])
with top_c3:
    export_format = st.radio("Download Format", ["PDF", "JPEG"], horizontal=True)

st.divider()

# ── Helper: force immediate rerun so values apply without Enter ───────
def _trigger_rerun():
    """Callback attached to every text_input; Streamlit re-reads the
    widget value on every keystroke change, so the credential list is
    always up-to-date without the user pressing Enter."""
    pass  # presence of on_change already forces a rerun cycle

# ── 3-Column Grid for the 15 Applications ─────────────────────────────
collected_credentials = []
grid_cols = st.columns(3)

for idx, app in enumerate(APPLICATIONS):
    col = grid_cols[idx % 3]
    with col:
        with st.container(border=True):
            st.markdown(f'<div class="card-title">{idx + 1}. {app["title"]}</div>', unsafe_allow_html=True)
            # Constant Identifier (Locked)
            st.text_input(
                f"{app['id_label']} (Constant)",
                value=app["id_value"],
                disabled=True,
                key=f"const_{idx}",
            )
            # Dynamic Branch Inputs – on_change ensures auto-apply
            uname = st.text_input(
                "Username",
                key=f"user_{idx}",
                placeholder=f"{selected_branch} username",
                on_change=_trigger_rerun,
            )
            upass = st.text_input(
                "Password",
                key=f"pass_{idx}",
                type="password",
                placeholder="••••••••",
                on_change=_trigger_rerun,
            )

            collected_credentials.append(
                {
                    "title": app["title"],
                    "id_label": app["id_label"],
                    "id_value": app["id_value"],
                    "username": uname.strip(),
                    "password": upass.strip(),
                }
            )

st.divider()

# ── Validation & Stateless In-Memory Export ────────────────────────────
all_filled = all(item["username"] and item["password"] for item in collected_credentials)
any_filled = any(item["username"] or item["password"] for item in collected_credentials)

btn_col1, btn_col2 = st.columns([2, 1])
with btn_col1:
    allow_partial = st.checkbox("Allow download even if some of the 15 cards are left blank", value=False)

can_download = all_filled or (allow_partial and any_filled)

if can_download:
    file_bytes, mime_type, ext = build_credential_grid(
        zone=selected_zone,
        branch=selected_branch,
        credentials=collected_credentials,
        fmt=export_format,
    )
    st.download_button(
        label=f"Download {selected_branch} ({selected_zone}) Credentials as {export_format}",
        data=file_bytes,
        file_name=f"Credentials_{selected_zone}_{selected_branch}.{ext}".replace(" ", "_"),
        mime=mime_type,
        type="primary",
        use_container_width=True,
    )
else:
    st.warning("Fill in all 15 Username & Password pairs (or check 'Allow download even if some cards are blank') to unlock the download button.")
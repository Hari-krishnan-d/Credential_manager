# config.py

THEME = {
    "gold": "#AA832B",
    "gold_light": "#C9A84C",
    "white": "#FFFFFF",
    "text": "#2B2B2B",
    "bg": "#FFF8EE",
    "card": "#FFFFFF",
}

ZONES_AND_BRANCHES = {
    "South Zone": ["Tiruppur", "Coimbatore", "Chennai", "Madurai", "Erode", "Thirunelveli"],
    "North Zone": ["Delhi", "Noida", "Jaipur", "Ludhiana"],
    "West Zone": ["Mumbai", "Surat", "Ahmedabad", "Pune"],
    "East Zone": ["Kolkata", "Bhubaneswar"],
}

# Flat branch list & reverse lookup  (branch → zone)
ALL_BRANCHES = [br for branches in ZONES_AND_BRANCHES.values() for br in branches]
BRANCH_TO_ZONE = {
    br: zone for zone, branches in ZONES_AND_BRANCHES.items() for br in branches
}

# ── 15 Applications ──────────────────────────────────────────────────
# Each app has:
#   title      – card heading
#   subtitle   – optional second line in the heading (e.g. "CRM & Loyalty App")
#   constants  – list of {label, value}  → shown as read-only
#   fields     – list of {label, type}   → editable; type = "text" | "password"
APPLICATIONS = [
    {
        "title": "SSO Application",
        "constants": [{"label": "URL", "value": "https://apps.wondrdiamonds.com"}],
        "fields": [
            {"label": "USERNAME", "type": "text"},
            {"label": "PASSWORD", "type": "password"},
        ],
    },
    {
        "title": "Cloud ERP Server",
        "constants": [{"label": "SERVER", "value": "erp.wondrdiamonds.com:51044"}],
        "fields": [
            {"label": "USERNAME", "type": "text"},
            {"label": "PASSWORD", "type": "password"},
        ],
    },
    {
        "title": "ERP Login (SJE Plus)",
        "constants": [],
        "fields": [
            {"label": "COMPANY", "type": "text"},
            {"label": "USERNAME", "type": "text"},
            {"label": "PASSWORD", "type": "password"},
        ],
    },
    {
        "title": "RFID Device",
        "constants": [],
        "fields": [
            {"label": "USERNAME", "type": "text"},
            {"label": "PIN", "type": "password"},
        ],
    },
    {
        "title": "Tiara Hub",
        "constants": [{"label": "URL", "value": "hub.tiara.jewelry"}],
        "fields": [
            {"label": "USERNAME", "type": "text"},
            {"label": "PASSWORD", "type": "password"},
        ],
    },
    {
        "title": "Zithara",
        "subtitle": "CRM & Loyalty App",
        "constants": [
            {"label": "URL", "value": "app.zithara.com"},
            {"label": "MOBILE APP", "value": "Zithara.ai"},
        ],
        "fields": [],
    },
    {
        "title": "Outlook Mail",
        "constants": [{"label": "PORTAL", "value": "https://outlook.office365.com/mail/"}],
        "fields": [
            {"label": "USERNAME", "type": "text"},
            {"label": "PASSWORD", "type": "password"},
            {"label": "REGISTERED MOBILE", "type": "text"},
        ],
    },
    {
        "title": "Biometric Attendance",
        "subtitle": "Reception system",
        "constants": [],
        "fields": [
            {"label": "USERNAME", "type": "text"},
            {"label": "PASSWORD", "type": "password"},
        ],
    },
    {
        "title": "Staff WIFI",
        "constants": [],
        "fields": [
            {"label": "NETWORK", "type": "text"},
            {"label": "PASSWORD", "type": "password"},
        ],
    },
    {
        "title": "Guest WIFI",
        "constants": [],
        "fields": [
            {"label": "NETWORK", "type": "text"},
            {"label": "PASSWORD", "type": "password"},
        ],
    },
    {
        "title": "Chit Login",
        "subtitle": "adwayit / eSip",
        "constants": [{"label": "URL", "value": "esip.adwayit.com"}],
        "fields": [
            {"label": "BRANCH", "type": "text"},
            {"label": "USERNAME", "type": "text"},
            {"label": "PASSWORD", "type": "password"},
        ],
    },
    {
        "title": "Gift Card Login",
        "subtitle": "adwayit / GVMS",
        "constants": [{"label": "URL", "value": "https://gms.adwayit.com"}],
        "fields": [
            {"label": "BRANCH", "type": "text"},
            {"label": "USERNAME", "type": "text"},
            {"label": "PASSWORD", "type": "password"},
        ],
    },
    {
        "title": "Estimation Link",
        "constants": [{"label": "URL", "value": "https://erp.wondrdiamonds.com:8044/Reports"}],
        "fields": [
            {"label": "USERNAME", "type": "text"},
            {"label": "PASSWORD", "type": "password"},
        ],
    },
    {
        "title": "Website Link",
        "constants": [{"label": "URL", "value": "https://www.wondrdiamonds.com"}],
        "fields": [],
    },
    {
        "title": "Chat Application",
        "constants": [{"label": "URL", "value": "https://chat.wondrdiamonds.com"}],
        "fields": [
            {"label": "USERNAME", "type": "text"},
            {"label": "PASSWORD", "type": "password"},
        ],
    },
]

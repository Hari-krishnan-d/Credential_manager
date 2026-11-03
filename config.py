# config.py

THEME = {
    "gold": "#AA832B",
    "white": "#FFFFFF",
    "dark": "#0F1724",
    "card": "#1A2332",
}

ZONES_AND_BRANCHES = {
    "South Zone": ["Tiruppur", "Coimbatore", "Chennai", "Madurai", "Erode"],
    "North Zone": ["Delhi", "Noida", "Jaipur", "Ludhiana"],
    "West Zone": ["Mumbai", "Surat", "Ahmedabad", "Pune"],
    "East Zone": ["Kolkata", "Bhubaneswar"],
}

# 15 Applications with constant URL / Company identifiers
APPLICATIONS = [
    {"title": "SSO Application", "id_label": "URL", "id_value": "https://sso.company.com/login"},
    {"title": "Cloud ERP Server", "id_label": "URL", "id_value": "https://clouderp.company.com:8443"},
    {"title": "ERP Login (SJE Plus)", "id_label": "Company", "id_value": "SJE_PLUS_CORP"},
    {"title": "HRMS & Payroll Portal", "id_label": "URL", "id_value": "https://hrms.company.com/sso"},
    {"title": "Webmail ( Zimbra / O365 )", "id_label": "URL", "id_value": "https://mail.company.com"},
    {"title": "GST & E-Way Bill Portal", "id_label": "URL", "id_value": "https://ewaybillgst.gov.in"},
    {"title": "CRM Portal", "id_label": "URL", "id_value": "https://crm.company.com"},
    {"title": "WMS / Inventory System", "id_label": "URL", "id_value": "https://wms.company.com/branch"},
    {"title": "POS Billing Terminal", "id_label": "Company", "id_value": "POS_RETAIL_NODE"},
    {"title": "Biometric Attendance", "id_label": "URL", "id_value": "https://bio.company.com:9090"},
    {"title": "Helpdesk & IT Ticketing", "id_label": "URL", "id_value": "https://support.company.com"},
    {"title": "DMS (Document Server)", "id_label": "URL", "id_value": "https://dms.company.com/vault"},
    {"title": "Firewall / VPN Gateway", "id_label": "URL", "id_value": "https://vpn.company.com:10443"},
    {"title": "Vendor & Dispatch Portal", "id_label": "URL", "id_value": "https://vendor.company.com"},
    {"title": "BI Analytics Dashboard", "id_label": "URL", "id_value": "https://bi.company.com/reports"},
]
import base64
import re
from datetime import datetime
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image, ImageDraw, ImageOps
import streamlit as st
from streamlit_autorefresh import st_autorefresh


# ==================================================
# ICON SET (เส้นบาง แบบ minimal, ไม่ใช้ emoji)
# ==================================================
ICONS = {
    "records": """<path d="M7 3h7l4 4v13a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/>
        <path d="M14 3v4h4"/><path d="M9 12h6M9 15.5h6M9 8.5h3"/>""",
    "users": """<circle cx="8.5" cy="8" r="3"/>
        <path d="M2.5 19.5c0-3.3 2.7-6 6-6s6 2.7 6 6"/>
        <circle cx="17" cy="9" r="2.4"/><path d="M15.2 13.3c2.5.4 4.3 2.5 4.3 5.2"/>""",
    "trending": """<path d="M3 17l6-6 4 4 8-8"/><path d="M15 6h6v6"/>""",
    "signal": """<path d="M2 8.5a15 15 0 0 1 20 0"/>
        <path d="M5.5 12a10 10 0 0 1 13 0"/>
        <path d="M9 15.5a5 5 0 0 1 6 0"/><circle cx="12" cy="19" r="1" fill="currentColor" stroke="none"/>""",
    "clock": """<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>""",
    "download": """<path d="M12 3v12"/><path d="M7 11l5 5 5-5"/><path d="M4 19h16"/>""",
    "door": """<path d="M5 21V4.5L15 3v18"/><path d="M15 3l4 1.2V21"/>
        <path d="M5 21h14"/><circle cx="12" cy="12.5" r="0.8" fill="currentColor" stroke="none"/>""",
    "peak": """<path d="M3 20h18"/><path d="M5 20l4-9 4 5 3-6 3 10"/>""",
    "classroom": """<path d="M6 21V6l7-3v18"/><path d="M13 21V9l5 2v10"/>
        <path d="M9 9h.01M9 12h.01M9 15h.01"/>""",
    "up": """<path d="M6 15l6-6 6 6"/>""",
    "down": """<path d="M6 9l6 6 6-6"/>""",
    "flame": """<path d="M12 2c1 4-4 5-4 9a4 4 0 0 0 8 0c0-1.5-1-2.3-1-3.6 1.6 1 2.5 3 2.5 4.9A5.5 5.5 0 0 1 12 22a5.5 5.5 0 0 1-5.5-5.7C6.5 12 9 9.5 12 2z"/>""",
}


def icon_svg(name: str, size: int = 18, color: str = "currentColor") -> str:
    body = ICONS.get(name, "")
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="1.6" stroke-linecap="round" '
        f'stroke-linejoin="round">{body}</svg>'
    )


def clean_html(html: str) -> str:
    """ลบช่องว่างต้นบรรทัดที่เกินมา เพื่อป้องกันไม่ให้ Streamlit/Markdown
    ตีความ HTML ที่เรา generate ว่าเป็น "code block" (ต้นเหตุที่ทำให้เห็นแท็ก
    <div class="bar-row"> ฯลฯ โผล่มาเป็นข้อความดิบแทนที่จะ render ปกติ).
    ใช้ครอบทุกก้อน HTML ก่อนส่งเข้า st.markdown(unsafe_allow_html=True) เสมอ"""
    lines = [ln.lstrip() for ln in html.strip("\n").split("\n")]
    return "\n".join(lines)


def image_to_base64(path: str) -> str:
    """แปลงไฟล์รูปเป็น base64 data URI เพื่อฝังลงใน HTML บล็อกเดียว
    (ป้องกันปัญหา div ที่เปิด-ปิดคนละ st.markdown แล้ว browser auto-close ก่อนเวลา)"""
    p = Path(path)
    if not p.exists():
        return ""
    try:
        data = p.read_bytes()
        ext = p.suffix.lstrip(".").lower() or "png"
        return f"data:image/{ext};base64,{base64.b64encode(data).decode()}"
    except Exception:
        return ""


def make_circular_favicon(path: str, size: int = 256):
    """ครอปรูปให้เป็นวงกลมโปร่งใส ใช้เฉพาะสำหรับ favicon เท่านั้น"""
    p = Path(path)
    if not p.exists():
        return None
    img = Image.open(p).convert("RGBA")
    img = ImageOps.fit(img, (size, size), Image.LANCZOS, centering=(0.5, 0.5))
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    img.putalpha(mask)
    return img


# ==================================================
# PAGE CONFIG
# ==================================================
FAVICON_PATH = Path(__file__).parent / "favicon.png"
_favicon = (
    make_circular_favicon(str(FAVICON_PATH)) if FAVICON_PATH.exists() else "▪"
)

st.set_page_config(
    page_title="Classroom Occupancy & Analytics Dashboard",
    page_icon=_favicon,
    layout="wide",
)

SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "14FJt332r41O2JvookMlfzIqljBPSJ1wdt08XnnkTl-8/"
    "export?format=csv"
)

# ==================================================
# THEME STATE
# ==================================================
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

KPI_PALETTES_LIGHT = [
    {"grad": "linear-gradient(135deg,#8B7CF6 0%,#6C4EF0 100%)", "icon_bg": "rgba(255,255,255,0.22)", "text": "#FFFFFF", "sub": "rgba(255,255,255,0.82)"},
    {"grad": "linear-gradient(135deg,#4FA3F7 0%,#2E6FE0 100%)", "icon_bg": "rgba(255,255,255,0.22)", "text": "#FFFFFF", "sub": "rgba(255,255,255,0.82)"},
    {"grad": "linear-gradient(135deg,#F76E9C 0%,#E8436F 100%)", "icon_bg": "rgba(255,255,255,0.22)", "text": "#FFFFFF", "sub": "rgba(255,255,255,0.82)"},
    {"grad": "linear-gradient(135deg,#FFB35A 0%,#F5862C 100%)", "icon_bg": "rgba(255,255,255,0.22)", "text": "#FFFFFF", "sub": "rgba(255,255,255,0.82)"},
]
KPI_PALETTES_DARK = [
    {"grad": "linear-gradient(135deg,#7B6EF0 0%,#5A3FE0 100%)", "icon_bg": "rgba(255,255,255,0.16)", "text": "#F3F1FF", "sub": "rgba(243,241,255,0.78)"},
    {"grad": "linear-gradient(135deg,#3E86D6 0%,#2159B8 100%)", "icon_bg": "rgba(255,255,255,0.16)", "text": "#EAF3FF", "sub": "rgba(234,243,255,0.78)"},
    {"grad": "linear-gradient(135deg,#DA5D89 0%,#B93A61 100%)", "icon_bg": "rgba(255,255,255,0.16)", "text": "#FFF0F5", "sub": "rgba(255,240,245,0.78)"},
    {"grad": "linear-gradient(135deg,#E69A44 0%,#C36F1C 100%)", "icon_bg": "rgba(255,255,255,0.16)", "text": "#FFF6EA", "sub": "rgba(255,246,234,0.78)"},
]

THEMES = {
    "Light": {
        "bg": "#F4F6FA",
        "bg_gradient": "radial-gradient(circle at 15% 0%, rgba(108,78,240,0.08) 0%, rgba(108,78,240,0) 40%), radial-gradient(circle at 85% 10%, rgba(11,37,69,0.06) 0%, rgba(11,37,69,0) 45%), #F4F6FA",
        "surface": "#FFFFFF",
        "surface_alpha": "rgba(255,255,255,0.72)",
        "border": "#E4E7EC",
        "text": "#101828",
        "subtitle": "#667085",
        "primary": "#0B2545",
        "accent": "#6C4EF0",
        "accent_soft": "rgba(108,78,240,0.12)",
        "sidebar_grad": "linear-gradient(180deg,#6C4EF0 0%,#3A2494 100%)",
        "chart_bg": "rgba(0,0,0,0)",
        "chart_grid": "#E2E6ED",
        "chart_font": "#334155",
        "plotly_template": "plotly_white",
        "line_color": "#6C4EF0",
        "marker_color": "#F5862C",
        "area_color": "#2451A6",
        "bar_scale": [[0, "#D9CFFB"], [0.5, "#8B7CF6"], [1, "#6C4EF0"]],
        "donut_colors": ["#6C4EF0", "#2E6FE0", "#E8436F", "#F5862C", "#2FBF71", "#0DB4C9", "#C2410C", "#7C3AED"],
        "footer_bg": "#FFFFFF",
        "success": "#15803D",
        "danger": "#B42318",
        "btn_bg": "#6C4EF0",
        "btn_text": "#FFFFFF",
        "btn_border": "#6C4EF0",
        "btn_hover_border": "#F5862C",
        "btn_hover_text": "#FFFFFF",
        "shadow": "0 1px 2px rgba(16,24,40,0.04), 0 8px 24px rgba(16,24,40,0.06)",
        "shadow_hover": "0 4px 10px rgba(16,24,40,0.06), 0 16px 36px rgba(16,24,40,0.10)",
        "kpi_palettes": KPI_PALETTES_LIGHT,
    },
    "Dark": {
        "bg": "#080B14",
        "bg_gradient": "radial-gradient(circle at 12% 0%, rgba(123,110,240,0.12) 0%, rgba(123,110,240,0) 40%), radial-gradient(circle at 88% 8%, rgba(110,168,254,0.10) 0%, rgba(110,168,254,0) 45%), #080B14",
        "surface": "#10162A",
        "surface_alpha": "rgba(16,22,42,0.72)",
        "border": "#212B45",
        "text": "#E7EBF3",
        "subtitle": "#8B96AC",
        "primary": "#6EA8FE",
        "accent": "#9C8CFB",
        "accent_soft": "rgba(156,140,251,0.14)",
        "sidebar_grad": "linear-gradient(180deg,#2C1F6B 0%,#0A0E1A 100%)",
        "chart_bg": "rgba(0,0,0,0)",
        "chart_grid": "#212B45",
        "chart_font": "#E7EBF3",
        "plotly_template": "plotly_dark",
        "line_color": "#9C8CFB",
        "marker_color": "#E69A44",
        "area_color": "#3B6FD6",
        "bar_scale": [[0, "#3A4569"], [0.5, "#7B6EF0"], [1, "#9C8CFB"]],
        "donut_colors": ["#9C8CFB", "#6EA8FE", "#DA5D89", "#E69A44", "#4ADE80", "#22D3EE", "#FB923C", "#C084FC"],
        "footer_bg": "#10162A",
        "success": "#4ADE80",
        "danger": "#F87171",
        "btn_bg": "#9C8CFB",
        "btn_text": "#0A0E1A",
        "btn_border": "#9C8CFB",
        "btn_hover_border": "#E69A44",
        "btn_hover_text": "#0A0E1A",
        "shadow": "0 1px 2px rgba(0,0,0,0.3), 0 8px 24px rgba(0,0,0,0.35)",
        "shadow_hover": "0 4px 10px rgba(0,0,0,0.35), 0 20px 44px rgba(0,0,0,0.45)",
        "kpi_palettes": KPI_PALETTES_DARK,
    },
}


def apply_theme_css(t: dict):
    st.markdown(
        clean_html(
            f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap" rel="stylesheet">

    <style>
    @property --angle {{
        syntax: '<angle>';
        initial-value: 0deg;
        inherits: false;
    }}
    @keyframes rotateBorder {{
        to {{ --angle: 360deg; }}
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    header[data-testid="stHeader"],
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    header {{
        background-color: transparent !important;
        background-image: none !important;
    }}
    header[data-testid="stHeader"] button {{ color: {t['text']} !important; }}

    html, body, p, span, div, label, h1, h2, h3, h4, h5, h6,
    button, input, select, textarea, a {{
        font-family: 'Kanit', sans-serif;
    }}
    [data-testid*="Icon"],
    [class*="material-symbols"],
    [class*="material-icon"],
    span[class*="eyeicon"] {{
        font-family: 'Material Symbols Outlined', 'Material Symbols Rounded',
                     'Material Icons', sans-serif !important;
        font-feature-settings: 'liga' !important;
        -webkit-font-feature-settings: 'liga' !important;
    }}
    .mono {{ font-family: 'IBM Plex Mono', monospace; }}

    .stApp {{ background: {t['bg_gradient']}; color: {t['text']}; }}

    div[data-testid="stAppViewContainer"] .main .block-container {{
        padding-top: 0.6rem;
        padding-bottom: 0.8rem;
    }}
    div[data-testid="stVerticalBlock"] {{ gap: 0.4rem; }}
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {{ gap: 0.3rem; }}
    section[data-testid="stSidebar"] .block-container {{
        padding-top: 1.2rem;
    }}

    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes growBar {{
        from {{ width: 0%; }}
        to {{ width: var(--w); }}
    }}
    @keyframes shimmer {{
        0% {{ background-position: -200% 0; }}
        100% {{ background-position: 200% 0; }}
    }}

    /* ---------- เส้นกรอบ "วาดสด" อัตโนมัติ แทนเส้นทึบธรรมดา ---------- */
    .live-border,
    div[data-testid="stPlotlyChart"],
    div[data-testid="stExpander"] {{
        position: relative;
    }}
    .live-border::before,
    div[data-testid="stPlotlyChart"]::before,
    div[data-testid="stExpander"]::before {{
        content: "";
        position: absolute;
        inset: 0;
        border-radius: inherit;
        padding: 1.4px;
        background: conic-gradient(from var(--angle), transparent 0%, {t['accent']} 10%, {t['marker_color']} 16%, transparent 26%, transparent 100%);
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        animation: rotateBorder 3.6s linear infinite;
        pointer-events: none;
    }}

    /* ---------- Header ---------- */
    .app-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        flex-wrap: wrap;
        background: {t['surface']};
        border: 1px solid {t['border']};
        border-radius: 14px;
        padding: 10px 18px;
        margin-bottom: 8px;
        box-shadow: {t['shadow']};
        animation: fadeInUp 0.5s ease-out;
        position: relative;
        overflow: hidden;
    }}
    .app-header::after {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, {t['accent']}, transparent, {t['accent']});
        background-size: 200% 100%;
        animation: shimmer 4s linear infinite;
    }}
    .app-header-left {{
        display: flex;
        align-items: center;
        gap: 14px;
        min-width: 0;
    }}
    .app-header-logo {{
        width: 44px;
        height: 44px;
        border-radius: 50%;
        object-fit: cover;
        flex-shrink: 0;
    }}
    .hero-eyebrow {{
        display: inline-flex;
        align-items: center;
        gap: 7px;
        font-size: 10.5px;
        font-weight: 500;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: {t['accent']};
        margin-bottom: 2px;
    }}
    .hero-eyebrow .dot {{
        width: 6px; height: 6px; border-radius: 50%;
        background: {t['accent']};
    }}
    .title-main {{
        font-size: 19px;
        font-weight: 600;
        color: {t['text']};
        line-height: 1.25;
        letter-spacing: -0.2px;
    }}
    .subtitle-main {{
        font-size: 12px;
        color: {t['subtitle']};
        font-weight: 400;
        margin-top: 2px;
    }}
    .status-pill {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: {t['bg']};
        border: 1px solid {t['border']};
        border-radius: 20px;
        padding: 6px 14px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11.5px;
        color: {t['text']};
        flex-shrink: 0;
    }}

    /* ---------- Live status strip ---------- */
    .status-strip {{
        display: flex;
        align-items: center;
        gap: 16px;
        background: {t['surface_alpha']};
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid {t['border']};
        border-radius: 10px;
        padding: 7px 14px;
        margin: 8px 0 10px 0;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        color: {t['subtitle']};
        flex-wrap: wrap;
        box-shadow: {t['shadow']};
    }}
    .status-strip .divider {{
        width: 1px; height: 13px; background: {t['border']};
    }}
    .status-item {{ display: flex; align-items: center; gap: 6px; }}
    .status-item svg {{ flex-shrink: 0; }}
    .status-online-dot {{
        width: 7px; height: 7px; border-radius: 50%;
        background: {t['success']};
        box-shadow: 0 0 0 3px rgba(21,128,61,0.15);
        animation: pulse-dot 2s ease-in-out infinite;
    }}
    .status-offline-dot {{
        width: 7px; height: 7px; border-radius: 50%;
        background: {t['danger']};
        box-shadow: 0 0 0 3px rgba(180,35,24,0.15);
    }}
    @keyframes pulse-dot {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.45; }}
    }}
    .status-label {{
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 500;
        color: {t['text']};
    }}

    /* ---------- KPI cards ---------- */
    .kpi-card {{
        position: relative;
        border-radius: 14px;
        padding: 12px 14px;
        height: 100%;
        box-shadow: {t['shadow']};
        overflow: hidden;
        transition: box-shadow 0.25s ease, transform 0.25s ease;
        animation: fadeInUp 0.5s ease-out backwards;
    }}
    div[data-testid="column"]:nth-of-type(1) .kpi-card {{ animation-delay: 0s; }}
    div[data-testid="column"]:nth-of-type(2) .kpi-card {{ animation-delay: 0.08s; }}
    div[data-testid="column"]:nth-of-type(3) .kpi-card {{ animation-delay: 0.16s; }}
    div[data-testid="column"]:nth-of-type(4) .kpi-card {{ animation-delay: 0.24s; }}
    .kpi-card::after {{
        content: "";
        position: absolute;
        top: -60%; left: -20%;
        width: 60%; height: 220%;
        background: rgba(255,255,255,0.10);
        transform: rotate(20deg);
        pointer-events: none;
    }}
    .kpi-card:hover {{
        box-shadow: {t['shadow_hover']};
        transform: translateY(-3px);
    }}
    .kpi-top {{
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 6px;
    }}
    .kpi-icon {{
        width: 32px; height: 32px;
        display: flex; align-items: center; justify-content: center;
        border-radius: 9px;
    }}
    .kpi-label {{
        font-size: 11.5px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        opacity: 0.9;
    }}
    .kpi-value {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 25px;
        font-weight: 600;
        letter-spacing: -0.5px;
    }}
    .kpi-delta {{
        font-size: 12px;
        font-weight: 500;
        margin-top: 4px;
        opacity: 0.9;
    }}

    /* ---------- Chart container ---------- */
    div[data-testid="stPlotlyChart"] {{
        background: {t['surface']};
        border-radius: 14px;
        padding: 10px 12px;
        box-shadow: {t['shadow']};
    }}

    /* ---------- Section headers ---------- */
    .section-head {{
        display: flex; align-items: center; gap: 9px;
        margin: 2px 0 6px 0;
    }}
    .section-bar {{
        width: 3px; height: 16px; border-radius: 2px;
        background: linear-gradient(180deg, {t['accent']}, {t['primary']});
        flex-shrink: 0;
    }}
    .section-title {{
        font-size: 15.5px; font-weight: 600; color: {t['text']};
    }}
    .section-sub {{
        font-size: 12px; color: {t['subtitle']}; margin-left: 12px;
    }}

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {{
        background: {t['sidebar_grad']};
        border-right: 1px solid rgba(255,255,255,0.06);
    }}
    section[data-testid="stSidebar"] *:not(input):not(select):not(textarea):not([data-baseweb="select"] *) {{
        color: #EDF1F7 !important;
    }}
    section[data-testid="stSidebar"] .stTextInput input,
    section[data-testid="stSidebar"] .stDateInput input,
    section[data-testid="stSidebar"] .stDateInput *,
    section[data-testid="stSidebar"] [data-baseweb="datepicker"] *,
    section[data-testid="stSidebar"] [data-baseweb="input"] *,
    section[data-testid="stSidebar"] div[data-baseweb="select"] span,
    section[data-testid="stSidebar"] div[data-baseweb="select"] div,
    section[data-testid="stSidebar"] input {{
        color: #101828 !important;
        -webkit-text-fill-color: #101828 !important;
    }}
    section[data-testid="stSidebar"] input::placeholder {{
        color: #667085 !important;
        opacity: 1 !important;
    }}
    section[data-testid="stSidebar"] .stTextInput input,
    section[data-testid="stSidebar"] .stDateInput input,
    section[data-testid="stSidebar"] [data-baseweb="datepicker"],
    section[data-testid="stSidebar"] [data-baseweb="input"],
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
        background-color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 7px;
    }}
    .sidebar-eyebrow {{
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: rgba(237,241,247,0.55) !important;
        font-weight: 500;
        margin-top: 2px;
        margin-bottom: 2px;
    }}
    .sidebar-meta {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        color: rgba(237,241,247,0.75) !important;
        line-height: 1.7;
    }}
    .sidebar-brandline {{
        height: 1px;
        background: linear-gradient(90deg, rgba(255,255,255,0.35), rgba(255,255,255,0));
        margin: 8px 0;
        border: none;
    }}

    /* ---------- Footer ---------- */
    .footer-card {{
        text-align: center;
        background: {t['footer_bg']};
        border: 1px solid {t['border']};
        border-radius: 14px;
        padding: 12px;
        margin-top: 10px;
        color: {t['subtitle']};
        font-size: 12.5px;
        box-shadow: {t['shadow']};
    }}
    .footer-card b {{ color: {t['text']}; font-weight: 600; }}

    /* ---------- Animated share bars ---------- */
    .bar-track {{
        position: relative;
        height: 8px;
        border-radius: 6px;
        background: {t['bg']};
        overflow: hidden;
    }}
    .bar-fill {{
        height: 100%;
        border-radius: 6px;
        width: var(--w);
        animation: growBar 1.1s cubic-bezier(0.22, 1, 0.36, 1) backwards;
        position: relative;
        overflow: hidden;
    }}
    .bar-fill::after {{
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        background-size: 200% 100%;
        animation: shimmer 2.2s linear infinite;
    }}

    /* ---------- Room usage grid (แยกรายห้อง) ---------- */
    .room-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
        gap: 10px;
        margin-top: 2px;
    }}
    .room-card {{
        background: {t['surface']};
        border-radius: 14px;
        padding: 12px 14px;
        box-shadow: {t['shadow']};
        transition: transform 0.22s ease, box-shadow 0.22s ease;
        animation: fadeInUp 0.45s ease-out backwards;
    }}
    .room-card:hover {{
        transform: translateY(-3px);
        box-shadow: {t['shadow_hover']};
    }}
    .room-card-top {{
        display: flex;
        align-items: center;
        gap: 9px;
        margin-bottom: 9px;
    }}
    .room-card-icon {{
        width: 30px; height: 30px;
        border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        flex-shrink: 0;
    }}
    .room-card-name {{
        font-size: 13.5px;
        font-weight: 600;
        color: {t['text']};
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }}
    .room-card-pct {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 15px;
        font-weight: 700;
    }}
    .room-card-meta {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 8px;
        font-size: 11.5px;
        color: {t['subtitle']};
    }}
    .room-card-peak {{
        margin-top: 4px;
        font-size: 11px;
        color: {t['subtitle']};
        display: flex;
        align-items: center;
        gap: 5px;
    }}

    /* ---------- Expander ---------- */
    div[data-testid="stExpander"] {{
        background: {t['surface']};
        border-radius: 14px;
        box-shadow: {t['shadow']};
    }}
    div[data-testid="stExpander"] > details > summary,
    div[data-testid="stExpander"] [data-testid="stExpanderHeader"],
    div[data-testid="stExpander"] summary {{
        background: {t['surface']} !important;
        color: {t['text']} !important;
        font-weight: 500;
    }}
    div[data-testid="stExpander"] > details > summary *,
    div[data-testid="stExpander"] [data-testid="stExpanderHeader"] *,
    div[data-testid="stExpander"] summary *,
    div[data-testid="stExpander"] [data-testid="stMarkdownContainer"] p,
    div[data-testid="stExpander"] span,
    div[data-testid="stExpander"] label {{
        color: {t['text']} !important;
    }}
    div[data-testid="stExpander"] summary:hover,
    div[data-testid="stExpander"] summary:hover * {{
        color: {t['primary']} !important;
    }}

    h1,h2,h3,h4,h5,h6 {{ color: {t['text']} !important; }}
    label,p,span,div {{ color: {t['text']}; }}
    div.stDownloadButton > button {{
        background-color: {t['btn_bg']} !important;
        color: {t['btn_text']} !important;
        border: 1px solid {t['btn_border']} !important;
        border-radius: 9px !important;
        font-weight: 500 !important;
        padding: 10px 22px !important;
        box-shadow: {t['shadow']};
        transition: all 0.2s ease;
    }}
    div.stDownloadButton > button:hover {{
        border-color: {t['btn_hover_border']} !important;
        color: {t['btn_hover_text']} !important;
        transform: translateY(-1px);
        box-shadow: {t['shadow_hover']};
    }}

    @media (max-width: 768px) {{
        .title-main {{ font-size: 18px; }}
        .kpi-value {{ font-size: 21px; }}
        .status-strip {{ font-size: 11px; gap: 12px; }}
        .app-header {{ padding: 12px 14px; }}
        .room-grid {{ grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); }}
    }}
    </style>
    """
        ),
        unsafe_allow_html=True,
    )


def style_chart(fig, t: dict, height=360):
    fig.update_layout(
        template=t["plotly_template"],
        plot_bgcolor=t["chart_bg"],
        paper_bgcolor=t["chart_bg"],
        font=dict(color=t["chart_font"], family="Kanit"),
        xaxis=dict(
            showgrid=True,
            gridcolor=t["chart_grid"],
            title_font=dict(color=t["text"], size=13),
            tickfont=dict(color=t["subtitle"], size=11),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=t["chart_grid"],
            title_font=dict(color=t["text"], size=13),
            tickfont=dict(color=t["subtitle"], size=11),
        ),
        margin=dict(t=16, b=16, l=16, r=16),
        height=height,
        hoverlabel=dict(
            bgcolor=t["surface"], font_color=t["text"], font_family="Kanit"
        ),
    )
    return fig


def kpi_card(icon: str, label: str, value: str, delta: str, palette: dict) -> str:
    return clean_html(
        f"""
    <div class="kpi-card" style="background:{palette['grad']};">
        <div class="kpi-top">
            <div class="kpi-label" style="color:{palette['text']};">{label}</div>
            <div class="kpi-icon" style="background:{palette['icon_bg']};">
                {icon_svg(icon, 17, palette['text'])}
            </div>
        </div>
        <div class="kpi-value" style="color:{palette['text']};">{value}</div>
        <div class="kpi-delta" style="color:{palette['sub']};">{delta}</div>
    </div>
    """
    )


def section_header(text: str, sub: str = "") -> str:
    sub_html = f'<span class="section-sub">{sub}</span>' if sub else ""
    return clean_html(
        f"""
    <div class="section-head">
        <span class="section-bar"></span>
        <span class="section-title">{text}</span>
        {sub_html}
    </div>
    """
    )


def build_room_cards(df: pd.DataFrame, room_col: str, theme: dict) -> str:
    """สร้างการ์ดสัดส่วนการใช้งาน แยกเป็นรายห้องเรียนทีละห้อง (ไม่รวมภาพรวม)
    แต่ละการ์ดมี: % สัดส่วนของห้องนั้นเทียบยอดรวม, แถบสัดส่วนอนิเมชัน,
    จำนวนคน/จำนวนครั้งที่บันทึก, แนวโน้มเทียบครึ่งช่วงเวลาแรก-หลัง, และวันพีคของห้องนั้น"""
    grp = (
        df.groupby(room_col)["Person Count"]
        .agg(total="sum", records="count")
        .reset_index()
        .sort_values("total", ascending=False)
    )
    grand_total = grp["total"].sum()
    palette = theme["donut_colors"]

    dates_sorted = sorted(df["Date"].dropna().unique())
    mid_point = dates_sorted[len(dates_sorted) // 2] if len(dates_sorted) >= 2 else None

    cards = ""
    for i, row in grp.reset_index(drop=True).iterrows():
        room = row[room_col]
        total = row["total"]
        records = int(row["records"])
        pct = round(total / grand_total * 100, 1) if grand_total else 0
        color = palette[i % len(palette)]

        sub = df[df[room_col] == room]
        by_date = sub.groupby("Date")["Person Count"].sum()
        peak_val = int(by_date.max()) if not by_date.empty else 0
        peak_date = by_date.idxmax() if not by_date.empty else None
        peak_str = pd.to_datetime(peak_date).strftime("%d/%m") if peak_date is not None else "-"

        trend_html = ""
        if mid_point is not None:
            first = sub[sub["Date"] < mid_point]["Person Count"].sum()
            second = sub[sub["Date"] >= mid_point]["Person Count"].sum()
            if first > 0:
                change = round((second - first) / first * 100, 1)
            else:
                change = 100.0 if second > 0 else 0.0
            up = change >= 0
            trend_color = theme["success"] if up else theme["danger"]
            trend_icon = icon_svg("up" if up else "down", 11, trend_color)
            trend_html = (
                f'<span style="display:inline-flex;align-items:center;gap:2px;'
                f'color:{trend_color};font-weight:600;">{trend_icon}{abs(change)}%</span>'
            )

        cards += f"""
        <div class="room-card live-border">
            <div class="room-card-top">
                <div class="room-card-icon" style="background:{color}22;color:{color};">
                    {icon_svg('classroom', 16, color)}
                </div>
                <div class="room-card-name">{room}</div>
                <div class="room-card-pct" style="color:{color};">{pct}%</div>
            </div>
            <div class="bar-track">
                <div class="bar-fill" style="--w:{pct}%; background:{color};"></div>
            </div>
            <div class="room-card-meta">
                <span>{int(total):,} คน &middot; {records:,} ครั้ง</span>
                {trend_html}
            </div>
            <div class="room-card-peak">{icon_svg('flame', 12, theme['subtitle'])} พีค {peak_val:,} คน &middot; {peak_str}</div>
        </div>
        """
    return clean_html(f'<div class="room-grid">{cards}</div>')


def find_room_column(df: pd.DataFrame):
    """หาคอลัมน์ที่ระบุชื่อห้องเรียน/สถานที่ (ถ้ามีในชีท) เพื่อทำกราฟห้องเรียนยอดนิยม"""
    candidates = ["room", "ห้อง", "ห้องเรียน", "classroom", "location", "สถานที่"]
    for col in df.columns:
        if any(c in col.lower() or c in col for c in candidates):
            return col
    return None


@st.cache_data(ttl=30)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip()
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
    return df


# ==================================================
# SIDEBAR
# ==================================================
with st.sidebar:
    try:
        st.image("Logo-Songkla.png", width=80)
    except Exception:
        pass

    st.markdown(
        "<div style='font-weight:600;font-size:16px;margin-top:4px;'>Dashboard Controls</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='sidebar-eyebrow'>Display theme</div>", unsafe_allow_html=True)
    theme_choice = st.radio(
        "Display theme",
        options=["Light", "Dark"],
        index=0 if st.session_state.theme == "Light" else 1,
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state.theme = theme_choice
    theme = THEMES[theme_choice]

    st.markdown("<hr class='sidebar-brandline'/>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-eyebrow'>Auto-refresh interval</div>", unsafe_allow_html=True)
    refresh_seconds = st.selectbox(
        "Auto-refresh interval",
        options=[10, 30, 60, 120],
        index=1,
        format_func=lambda s: f"{s} s",
        label_visibility="collapsed",
    )

    date_range = None
    st.markdown("<div class='sidebar-eyebrow'>Search</div>", unsafe_allow_html=True)
    search_query = st.text_input(
        "Search", placeholder="Search records...", label_visibility="collapsed"
    )

st_autorefresh(interval=refresh_seconds * 1000, key="auto_refresh")

apply_theme_css(theme)

# ==================================================
# LOAD DATA + STATUS
# ==================================================
system_online = True
load_error = ""
df = None
room_col = None
try:
    df = load_data()
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    room_col = find_room_column(df)
except Exception as e:
    system_online = False
    load_error = str(e)

# ==================================================
# HEADER
# ==================================================
logo_b64 = image_to_base64("logo_proj.png")
logo_img_html = f'<img src="{logo_b64}" class="app-header-logo" alt="logo">' if logo_b64 else ""
if system_online:
    status_dot = '<span class="status-online-dot"></span>'
    status_text = "Online"
else:
    status_dot = '<span class="status-offline-dot"></span>'
    status_text = "Offline"

st.markdown(
    clean_html(
        f"""
    <div class="app-header">
        <div class="app-header-left">
            {logo_img_html}
            <div>
                <div class="hero-eyebrow"><span class="dot"></span>REAL-TIME MONITORING</div>
                <div class="title-main">Classroom Occupancy &amp; Activity Monitoring Dashboard</div>
                <div class="subtitle-main">ระบบวิเคราะห์ข้อมูลการเข้า-ออกห้องเรียนภายในอาคารแบบเรียลไทม์ &middot; Faculty of Education, Prince of Songkla University</div>
            </div>
        </div>
        <div class="status-pill">{status_dot}<span style="text-transform:uppercase;letter-spacing:0.06em;">{status_text}</span></div>
    </div>
    """
    ),
    unsafe_allow_html=True,
)

if system_online:
    with st.sidebar:
        if "Date" in df.columns and not df["Date"].isnull().all():
            min_date = df["Date"].min().date()
            max_date = df["Date"].max().date()
            st.markdown("<div class='sidebar-eyebrow'>Date range</div>", unsafe_allow_html=True)
            date_range = st.date_input(
                "Date range", [min_date, max_date], label_visibility="collapsed"
            )
            if len(date_range) == 2:
                df = df[
                    (df["Date"] >= pd.to_datetime(date_range[0]))
                    & (df["Date"] <= pd.to_datetime(date_range[1]))
                ]

        if room_col:
            st.markdown("<div class='sidebar-eyebrow'>ห้องเรียน</div>", unsafe_allow_html=True)
            room_options = ["ทั้งหมด"] + sorted(df[room_col].dropna().unique().tolist())
            room_choice = st.selectbox("ห้องเรียน", options=room_options, label_visibility="collapsed")
            if room_choice != "ทั้งหมด":
                df = df[df[room_col] == room_choice]

        if search_query:
            df = df[
                df.astype(str)
                .apply(lambda x: x.str.contains(search_query, case=False))
                .any(axis=1)
            ]

        st.markdown("<hr class='sidebar-brandline'/>", unsafe_allow_html=True)
        st.markdown(
            clean_html(
                f"""<div class="sidebar-meta">
            RECORDS &nbsp; {len(df):,}<br>
            SYNCED &nbsp;&nbsp;&nbsp; {datetime.now().strftime('%H:%M:%S')}
            </div>"""
            ),
            unsafe_allow_html=True,
        )

    if df.empty:
        st.warning("No records match the selected filters. Adjust the date range or search term.")
        st.stop()

    # ==================================================
    # LIVE STATUS STRIP
    # ==================================================
    st.markdown(
        clean_html(
            f"""
        <div class="status-strip">
            <div class="status-item">{icon_svg('signal', 15)}<span>Data source: Google Sheets</span></div>
            <div class="divider"></div>
            <div class="status-item">{icon_svg('clock', 15)}<span>Last sync {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</span></div>
            <div class="divider"></div>
            <div class="status-item"><span>Refresh every {refresh_seconds}s</span></div>
            <div class="divider"></div>
            <div class="status-item"><span>{len(df):,} records</span></div>
        </div>
        """
        ),
        unsafe_allow_html=True,
    )

    # ==================================================
    # KPI CARDS
    # ==================================================
    total_records = len(df)
    has_count = "Person Count" in df.columns and pd.api.types.is_numeric_dtype(df["Person Count"])
    total_people = int(df["Person Count"].sum()) if has_count else 0

    peak_label = "—"
    peak_sub = "-"
    if has_count and "Date" in df.columns:
        daily_peak = df.groupby("Date")["Person Count"].sum()
        if not daily_peak.empty:
            peak_date = daily_peak.idxmax()
            peak_val = int(daily_peak.max())
            peak_label = f"{peak_val:,} คน"
            peak_sub = pd.to_datetime(peak_date).strftime("%d/%m/%Y")

    active_rooms = df[room_col].nunique() if room_col else None
    palettes = theme["kpi_palettes"]

    if room_col:
        c1, c2, c3, c4 = st.columns(4)
        cols_kpi = [c1, c2, c3, c4]
    else:
        c1, c2, c3 = st.columns(3)
        cols_kpi = [c1, c2, c3]

    with cols_kpi[0]:
        st.markdown(kpi_card("records", "Total Records", f"{total_records:,}", "รายการทั้งหมด", palettes[0]), unsafe_allow_html=True)
    with cols_kpi[1]:
        st.markdown(kpi_card("users", "Total Occupancy", f"{total_people:,}", "ยอดสะสมรวม (ห้องเรียน)", palettes[1]), unsafe_allow_html=True)
    with cols_kpi[2]:
        st.markdown(kpi_card("peak", "Peak Day", peak_label, f"วันที่ {peak_sub}", palettes[2]), unsafe_allow_html=True)
    if room_col:
        with cols_kpi[3]:
            st.markdown(kpi_card("door", "Active Classrooms", f"{active_rooms:,}", "ห้องเรียนที่มีการใช้งาน", palettes[3]), unsafe_allow_html=True)

    # ==================================================
    # TREND LINE (full width)
    # ==================================================
    if "Date" in df.columns and "Person Count" in df.columns:
        daily = df.groupby("Date")["Person Count"].sum().reset_index().sort_values("Date")

        st.markdown(
            section_header("แนวโน้มการเข้า-ออกห้องเรียนรายวัน", "Classroom Access · Time Series Analysis"),
            unsafe_allow_html=True,
        )
        line_fig = px.line(
            daily, x="Date", y="Person Count", markers=True,
            color_discrete_sequence=[theme["line_color"]],
            labels={"Date": "วันที่", "Person Count": "จำนวนผู้เข้าใช้ห้องเรียน (คน)"},
        )
        line_fig.update_traces(
            line=dict(width=2.6, shape="spline"),
            marker=dict(size=6, color=theme["marker_color"]),
            fill="tozeroy",
            fillcolor=theme["accent_soft"],
        )
        st.plotly_chart(style_chart(line_fig, theme, 320), use_container_width=True)

        # ==================================================
        # ROOM-BY-ROOM USAGE (แยกรายห้อง ไม่รวมภาพรวม)
        # ==================================================
        if room_col:
            st.markdown(
                section_header("สัดส่วนการใช้งานแยกรายห้อง", "แต่ละห้องเทียบยอดรวมทั้งหมด · พร้อมแนวโน้มและวันพีค"),
                unsafe_allow_html=True,
            )
            st.markdown(build_room_cards(df, room_col, theme), unsafe_allow_html=True)

            st.markdown(
                section_header("สัดส่วนการใช้งานรายวัน", "Daily Distribution"),
                unsafe_allow_html=True,
            )
            bar_fig = px.bar(
                daily, x="Date", y="Person Count", color="Person Count",
                color_continuous_scale=theme["bar_scale"],
                labels={"Date": "วันที่", "Person Count": "จำนวนคน"},
            )
            bar_fig.update_traces(marker_line_width=0)
            bar_fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(style_chart(bar_fig, theme, 320), use_container_width=True)
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(section_header("สัดส่วนการใช้งานรายวัน", "Daily Distribution"), unsafe_allow_html=True)
                bar_fig = px.bar(
                    daily, x="Date", y="Person Count", color="Person Count",
                    color_continuous_scale=theme["bar_scale"],
                    labels={"Date": "วันที่", "Person Count": "จำนวนคน"},
                )
                bar_fig.update_traces(marker_line_width=0)
                bar_fig.update_layout(coloraxis_showscale=False)
                st.plotly_chart(style_chart(bar_fig, theme, 320), use_container_width=True)
            with col_b:
                st.markdown(section_header("ความหนาแน่นสะสม", "Cumulative Area Trend"), unsafe_allow_html=True)
                area_fig = px.area(
                    daily, x="Date", y="Person Count",
                    color_discrete_sequence=[theme["area_color"]],
                    labels={"Date": "วันที่", "Person Count": "จำนวนคน"},
                )
                st.plotly_chart(style_chart(area_fig, theme, 320), use_container_width=True)

    # ==================================================
    # FOOTER
    # ==================================================
    st.markdown(
        clean_html(
            f"""
        <div class="footer-card">
            <b>Classroom Occupancy &amp; Analytics Dashboard</b><br>
            Prince of Songkla University &middot; Faculty of Engineering<br>
            <span style="font-size: 12px;">
                Academic Project 2026 &middot; Streamlit &amp; Python &middot; Theme: {theme_choice}
            </span>
        </div>
        """
        ),
        unsafe_allow_html=True,
    )

else:
    st.error(
        f"ไม่สามารถเชื่อมต่อหรือโหลดข้อมูลจาก Google Sheets ได้ กรุณาตรวจสอบลิงก์ CSV หรือการเชื่อมอินเทอร์เน็ต (Error: {load_error})"
    )

from datetime import datetime
from pathlib import Path
import pandas as pd
import plotly.express as px
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
}


def icon_svg(name: str, size: int = 18) -> str:
    body = ICONS.get(name, "")
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
        f'stroke-linejoin="round">{body}</svg>'
    )


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
# THEME STATE — โทนพรีเมียม: เนวี่เข้ม + ทองบรอนซ์ + glass surface
# ==================================================
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

THEMES = {
    "Light": {
        "bg": "#F4F6FA",
        "bg_gradient": "radial-gradient(circle at 15% 0%, rgba(166,128,61,0.10) 0%, rgba(166,128,61,0) 40%), radial-gradient(circle at 85% 10%, rgba(11,37,69,0.08) 0%, rgba(11,37,69,0) 45%), #F4F6FA",
        "surface": "#FFFFFF",
        "surface_alpha": "rgba(255,255,255,0.72)",
        "border": "#E4E7EC",
        "text": "#101828",
        "subtitle": "#667085",
        "primary": "#0B2545",
        "accent": "#A6803D",
        "accent_soft": "rgba(166,128,61,0.14)",
        "sidebar_grad": "linear-gradient(180deg,#0B2545 0%,#061527 100%)",
        "chart_bg": "rgba(0,0,0,0)",
        "chart_grid": "#E2E6ED",
        "chart_font": "#334155",
        "plotly_template": "plotly_white",
        "line_color": "#0B2545",
        "marker_color": "#A6803D",
        "area_color": "#2451A6",
        "bar_scale": [[0, "#D9C79E"], [0.5, "#A6803D"], [1, "#0B2545"]],
        "footer_bg": "#FFFFFF",
        "success": "#15803D",
        "danger": "#B42318",
        "btn_bg": "#0B2545",
        "btn_text": "#FFFFFF",
        "btn_border": "#0B2545",
        "btn_hover_border": "#A6803D",
        "btn_hover_text": "#FFFFFF",
        "shadow": "0 1px 2px rgba(16,24,40,0.04), 0 8px 24px rgba(16,24,40,0.06)",
        "shadow_hover": "0 4px 10px rgba(16,24,40,0.06), 0 16px 36px rgba(16,24,40,0.10)",
    },
    "Dark": {
        "bg": "#080B14",
        "bg_gradient": "radial-gradient(circle at 12% 0%, rgba(217,184,113,0.10) 0%, rgba(217,184,113,0) 40%), radial-gradient(circle at 88% 8%, rgba(110,168,254,0.10) 0%, rgba(110,168,254,0) 45%), #080B14",
        "surface": "#10162A",
        "surface_alpha": "rgba(16,22,42,0.72)",
        "border": "#212B45",
        "text": "#E7EBF3",
        "subtitle": "#8B96AC",
        "primary": "#6EA8FE",
        "accent": "#D9B871",
        "accent_soft": "rgba(217,184,113,0.14)",
        "sidebar_grad": "linear-gradient(180deg,#0A0E1A 0%,#000000 100%)",
        "chart_bg": "rgba(0,0,0,0)",
        "chart_grid": "#212B45",
        "chart_font": "#E7EBF3",
        "plotly_template": "plotly_dark",
        "line_color": "#6EA8FE",
        "marker_color": "#D9B871",
        "area_color": "#3B6FD6",
        "bar_scale": [[0, "#3A4569"], [0.5, "#6EA8FE"], [1, "#D9B871"]],
        "footer_bg": "#10162A",
        "success": "#4ADE80",
        "danger": "#F87171",
        "btn_bg": "#D9B871",
        "btn_text": "#0A0E1A",
        "btn_border": "#D9B871",
        "btn_hover_border": "#6EA8FE",
        "btn_hover_text": "#0A0E1A",
        "shadow": "0 1px 2px rgba(0,0,0,0.3), 0 8px 24px rgba(0,0,0,0.35)",
        "shadow_hover": "0 4px 10px rgba(0,0,0,0.35), 0 20px 44px rgba(0,0,0,0.45)",
    },
}

def apply_theme_css(t: dict):
    st.markdown(
        f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap" rel="stylesheet">

    <style>
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

    /* ---------- Hero header ---------- */
    .hero-wrap {{
        position: relative;
        border-radius: 18px;
        padding: 26px 30px;
        margin-bottom: 20px;
        background: linear-gradient(120deg, {t['primary']} 0%, #133366 55%, {t['primary']} 100%);
        box-shadow: {t['shadow_hover']};
        overflow: hidden;
    }}
    .hero-wrap::before {{
        content: "";
        position: absolute;
        inset: 0;
        background:
            radial-gradient(circle at 92% -10%, rgba(166,128,61,0.35) 0%, rgba(166,128,61,0) 45%),
            radial-gradient(circle at 0% 120%, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0) 40%);
        pointer-events: none;
    }}
    .hero-eyebrow {{
        position: relative;
        display: inline-flex;
        align-items: center;
        gap: 7px;
        font-size: 11.5px;
        font-weight: 500;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: {t['accent']};
        margin-bottom: 8px;
    }}
    .hero-eyebrow .dot {{
        width: 6px; height: 6px; border-radius: 50%;
        background: {t['accent']};
    }}
    .title-main {{
        position: relative;
        font-size: 32px;
        font-weight: 600;
        color: #101828;
        line-height: 1.25;
        letter-spacing: -0.3px;
    }}
    .subtitle-main {{
        position: relative;
        font-size: 14px;
        color: rgba(255,255,255,0.68);
        font-weight: 300;
        margin-top: 6px;
    }}

    /* ---------- Live status strip ---------- */
    .status-strip {{
        display: flex;
        align-items: center;
        gap: 22px;
        background: {t['surface_alpha']};
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid {t['border']};
        border-radius: 10px;
        padding: 10px 18px;
        margin: 18px 0 22px 0;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12.5px;
        color: {t['subtitle']};
        flex-wrap: wrap;
        box-shadow: {t['shadow']};
    }}
    .status-strip .divider {{
        width: 1px; height: 14px; background: {t['border']};
    }}
    .status-item {{ display: flex; align-items: center; gap: 7px; }}
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
        background: {t['surface']};
        border: 1px solid {t['border']};
        border-radius: 14px;
        padding: 22px 22px 20px 22px;
        height: 100%;
        box-shadow: {t['shadow']};
        overflow: hidden;
        transition: box-shadow 0.25s ease, transform 0.25s ease;
    }}
    .kpi-card:hover {{
        box-shadow: {t['shadow_hover']};
        transform: translateY(-2px);
    }}
    .kpi-card::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, {t['accent']}, {t['primary']});
    }}
    .kpi-top {{
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 16px;
    }}
    .kpi-icon {{
        width: 38px; height: 38px;
        display: flex; align-items: center; justify-content: center;
        border-radius: 10px;
        background: {t['accent_soft']};
        color: {t['accent']};
    }}
    .kpi-label {{
        font-size: 12px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: {t['subtitle']};
    }}
    .kpi-value {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 32px;
        font-weight: 600;
        color: {t['text']};
        letter-spacing: -0.5px;
    }}
    .kpi-delta {{
        font-size: 12.5px;
        color: {t['accent']};
        font-weight: 500;
        margin-top: 6px;
    }}

    /* ---------- Chart container ---------- */
    div[data-testid="stPlotlyChart"] {{
        background: {t['surface']};
        border: 1px solid {t['border']};
        border-radius: 14px;
        padding: 18px;
        box-shadow: {t['shadow']};
    }}

    /* ---------- Section headers ---------- */
    .section-head {{
        display: flex; align-items: center; gap: 10px;
        margin: 6px 0 14px 0;
    }}
    .section-bar {{
        width: 3px; height: 18px; border-radius: 2px;
        background: linear-gradient(180deg, {t['accent']}, {t['primary']});
        flex-shrink: 0;
    }}
    .section-title {{
        font-size: 17px; font-weight: 600; color: {t['text']};
    }}
    .section-sub {{
        font-size: 12.5px; color: {t['subtitle']}; margin-left: 13px;
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
        margin-top: 4px;
    }}
    .sidebar-meta {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        color: rgba(237,241,247,0.75) !important;
        line-height: 1.9;
    }}
    .sidebar-brandline {{
        height: 1px;
        background: linear-gradient(90deg, rgba(217,184,113,0.6), rgba(217,184,113,0));
        margin: 16px 0;
        border: none;
    }}

    /* ---------- Footer ---------- */
    .footer-card {{
        text-align: center;
        background: {t['footer_bg']};
        border: 1px solid {t['border']};
        border-radius: 14px;
        padding: 20px;
        margin-top: 32px;
        color: {t['subtitle']};
        font-size: 13px;
        box-shadow: {t['shadow']};
    }}
    .footer-card b {{ color: {t['text']}; font-weight: 600; }}

    /* ---------- Expander ---------- */
    div[data-testid="stExpander"] {{
        background: {t['surface']};
        border: 1px solid {t['border']};
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
        .title-main {{ font-size: 22px; }}
        .kpi-value {{ font-size: 24px; }}
        .status-strip {{ font-size: 11px; gap: 14px; }}
        .hero-wrap {{ padding: 20px; }}
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )


def style_chart(fig, t: dict, height=380):
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
        margin=dict(t=20, b=20, l=20, r=20),
        height=height,
        hoverlabel=dict(
            bgcolor=t["surface"], font_color=t["text"], font_family="Kanit"
        ),
    )
    return fig


def kpi_card(icon: str, label: str, value: str, delta: str) -> str:
    return f"""
    <div class="kpi-card">
        <div class="kpi-top">
            <div class="kpi-label">{label}</div>
            <div class="kpi-icon">{icon_svg(icon, 18)}</div>
        </div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-delta">{delta}</div>
    </div>
    """


def section_header(text: str, sub: str = "") -> str:
    sub_html = f'<span class="section-sub">{sub}</span>' if sub else ""
    return f"""
    <div class="section-head">
        <span class="section-bar"></span>
        <span class="section-title">{text}</span>
        {sub_html}
    </div>
    """


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
        "<div style='font-weight:600;font-size:16px;margin-top:10px;'>"
        "Dashboard Controls</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='sidebar-eyebrow'>Display theme</div>", unsafe_allow_html=True
    )
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

    st.markdown(
        "<div class='sidebar-eyebrow'>Auto-refresh interval</div>",
        unsafe_allow_html=True,
    )
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
# HERO HEADER
# ==================================================
st.markdown('<div class="hero-wrap">', unsafe_allow_html=True)
col_logo, col_title, col_status = st.columns([1.2, 5.8, 2])

with col_logo:
    try:
        st.image("logo_proj.png", width=140)
    except Exception:
        pass

with col_title:
    st.markdown(
        """
        <div class="hero-eyebrow"><span class="dot"></span>REAL-TIME MONITORING</div>
        <div class="title-main">Classroom Occupancy &amp; Activity Monitoring Dashboard</div>
        <div class="subtitle-main">ระบบวิเคราะห์ข้อมูลการเข้า-ออกห้องเรียนภายในอาคารแบบเรียลไทม์ &middot; Faculty of Engineering, Prince of Songkla University</div>
        """,
        unsafe_allow_html=True,
    )

status_placeholder = col_status.empty()
st.markdown('</div>', unsafe_allow_html=True)

# ==================================================
# LOAD DATA + STATUS
# ==================================================
system_online = True
try:
    df = load_data()

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    room_col = find_room_column(df)

    with st.sidebar:
        if "Date" in df.columns and not df["Date"].isnull().all():
            min_date = df["Date"].min().date()
            max_date = df["Date"].max().date()
            st.markdown(
                "<div class='sidebar-eyebrow'>Date range</div>",
                unsafe_allow_html=True,
            )
            date_range = st.date_input(
                "Date range",
                [min_date, max_date],
                label_visibility="collapsed",
            )
            if len(date_range) == 2:
                df = df[
                    (df["Date"] >= pd.to_datetime(date_range[0]))
                    & (df["Date"] <= pd.to_datetime(date_range[1]))
                ]

        if room_col:
            st.markdown(
                "<div class='sidebar-eyebrow'>ห้องเรียน</div>", unsafe_allow_html=True
            )
            room_options = ["ทั้งหมด"] + sorted(df[room_col].dropna().unique().tolist())
            room_choice = st.selectbox(
                "ห้องเรียน", options=room_options, label_visibility="collapsed"
            )
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
            f"""<div class="sidebar-meta">
            RECORDS &nbsp; {len(df):,}<br>
            SYNCED &nbsp;&nbsp;&nbsp; {datetime.now().strftime('%H:%M:%S')}
            </div>""",
            unsafe_allow_html=True,
        )

    with status_placeholder:
        st.markdown(
            f"""
            <div style="display:flex;justify-content:flex-end;">
                <div style="display:flex;align-items:center;gap:8px;background:rgba(255,255,255,0.10);
                    border:1px solid rgba(255,255,255,0.18);border-radius:20px;padding:7px 16px;
                    font-family:'IBM Plex Mono',monospace;font-size:12px;color:#fff;">
                    <span class="status-online-dot"></span>
                    <span style="text-transform:uppercase;letter-spacing:0.06em;">Online</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if df.empty:
        st.warning("No records match the selected filters. Adjust the date range or search term.")
        st.stop()

    # ==================================================
    # LIVE STATUS STRIP
    # ==================================================
    st.markdown(
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
        """,
        unsafe_allow_html=True,
    )

    # ==================================================
    # KPI CARDS
    # ==================================================
    total_records = len(df)
    has_count = (
        "Person Count" in df.columns
        and pd.api.types.is_numeric_dtype(df["Person Count"])
    )
    total_people = int(df["Person Count"].sum()) if has_count else 0
    average_people = round(df["Person Count"].mean(), 2) if has_count else 0

    peak_label = "—"
    if has_count and "Date" in df.columns:
        daily_peak = df.groupby("Date")["Person Count"].sum()
        if not daily_peak.empty:
            peak_date = daily_peak.idxmax()
            peak_val = int(daily_peak.max())
            peak_label = f"{peak_val:,} คน"
            peak_sub = pd.to_datetime(peak_date).strftime("%d/%m/%Y")
        else:
            peak_sub = "-"
    else:
        peak_sub = "-"

    active_rooms = df[room_col].nunique() if room_col else None

    if room_col:
        c1, c2, c3, c4 = st.columns(4)
        cols_kpi = [c1, c2, c3, c4]
    else:
        c1, c2, c3 = st.columns(3)
        cols_kpi = [c1, c2, c3]

    with cols_kpi[0]:
        st.markdown(
            kpi_card("records", "Total Records", f"{total_records:,}", "รายการทั้งหมด"),
            unsafe_allow_html=True,
        )
    with cols_kpi[1]:
        st.markdown(
            kpi_card("users", "Total Occupancy", f"{total_people:,}", "ยอดสะสมรวม (ห้องเรียน)"),
            unsafe_allow_html=True,
        )
    with cols_kpi[2]:
        st.markdown(
            kpi_card("peak", "Peak Day", peak_label, f"วันที่ {peak_sub}"),
            unsafe_allow_html=True,
        )
    if room_col:
        with cols_kpi[3]:
            st.markdown(
                kpi_card("door", "Active Classrooms", f"{active_rooms:,}", "ห้องเรียนที่มีการใช้งาน"),
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ==================================================
    # CHARTS
    # ==================================================
    if "Date" in df.columns and "Person Count" in df.columns:
        daily = (
            df.groupby("Date")["Person Count"].sum().reset_index().sort_values("Date")
        )

        st.markdown(
            section_header(
                "แนวโน้มการเข้า-ออกห้องเรียนรายวัน",
                "Classroom Access · Time Series Analysis",
            ),
            unsafe_allow_html=True,
        )

        line_fig = px.line(
            daily,
            x="Date",
            y="Person Count",
            markers=True,
            color_discrete_sequence=[theme["line_color"]],
            labels={"Date": "วันที่", "Person Count": "จำนวนผู้เข้าใช้ห้องเรียน (คน)"},
        )
        line_fig.update_traces(
            line=dict(width=2.8, shape="spline"),
            marker=dict(size=7, color=theme["marker_color"]),
            fill="tozeroy",
            fillcolor=theme["accent_soft"],
        )
        st.plotly_chart(style_chart(line_fig, theme, 400), use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown(
                section_header(
                    "สัดส่วนการใช้งานรายวัน", "Daily Distribution"
                ),
                unsafe_allow_html=True,
            )
            bar_fig = px.bar(
                daily,
                x="Date",
                y="Person Count",
                color="Person Count",
                color_continuous_scale=theme["bar_scale"],
                labels={"Date": "วันที่", "Person Count": "จำนวนคน"},
            )
            bar_fig.update_traces(marker_line_width=0)
            bar_fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(
                style_chart(bar_fig, theme, 350), use_container_width=True
            )

        with col_b:
            if room_col:
                st.markdown(
                    section_header(
                        "ห้องเรียนยอดนิยม", "Top Classrooms by Usage"
                    ),
                    unsafe_allow_html=True,
                )
                room_summary = (
                    df.groupby(room_col)["Person Count"]
                    .sum()
                    .reset_index()
                    .sort_values("Person Count", ascending=True)
                    .tail()
                )
                room_fig = px.bar(
                    room_summary,
                    x="Person Count",
                    y=room_col,
                    orientation="h",
                    color="Person Count",
                    color_continuous_scale=theme["bar_scale"],
                    labels={"Person Count": "จำนวนคนสะสม", room_col: "ห้องเรียน"},
                )
                room_fig.update_traces(marker_line_width=0)
                room_fig.update_layout(coloraxis_showscale=False)
                st.plotly_chart(
                    style_chart(room_fig, theme, 350), use_container_width=True
                )
            else:
                st.markdown(
                    section_header(
                        "ความหนาแน่นสะสม", "Cumulative Area Trend"
                    ),
                    unsafe_allow_html=True,
                )
                area_fig = px.area(
                    daily,
                    x="Date",
                    y="Person Count",
                    color_discrete_sequence=[theme["area_color"]],
                    labels={"Date": "วันที่", "Person Count": "จำนวนคน"},
                )
                st.plotly_chart(
                    style_chart(area_fig, theme, 350), use_container_width=True
                )

    # ==================================================
    # EXPORT (ไม่แสดงตารางดิบ — มีเฉพาะปุ่มดาวน์โหลด)
    # ==================================================
    st.markdown("<br>", unsafe_allow_html=True)
    csv_data = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="⬇ Download full report (.CSV)",
        data=csv_data,
        file_name="Classroom_Monitoring_Report.csv",
        mime="text/csv",
    )

    # ==================================================
    # FOOTER
    # ==================================================
    st.markdown(
        f"""
        <div class="footer-card">
            <b>Classroom Occupancy &amp; Analytics Dashboard</b><br>
            Prince of Songkla University &middot; Faculty of Engineering<br>
            <span style="font-size: 12px;">
                Academic Project 2026 &middot; Streamlit &amp; Python &middot; Theme: {theme_choice}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

except Exception as e:
    system_online = False
    with status_placeholder:
        st.markdown(
            """
            <div style="display:flex;justify-content:flex-end;">
                <div style="display:flex;align-items:center;gap:8px;background:rgba(255,255,255,0.10);
                    border:1px solid rgba(255,255,255,0.18);border-radius:20px;padding:7px 16px;
                    font-family:'IBM Plex Mono',monospace;font-size:12px;color:#fff;">
                    <span class="status-offline-dot"></span>
                    <span style="text-transform:uppercase;letter-spacing:0.06em;">Offline / Error</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.error(f"ไม่สามารถเชื่อมต่อหรือโหลดข้อมูลจาก Google Sheets ได้ กรุณาตรวจสอบลิงก์ CSV หรือการเชื่อมอินเทอร์เน็ต (Error: {e})")
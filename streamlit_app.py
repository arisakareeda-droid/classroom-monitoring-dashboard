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
        f'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        f'stroke-linejoin="round">{body}</svg>'
    )


def make_circular_favicon(path: str, size: int = 256):
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
# THEME STATE — โทน Dashboard UI ทันสมัย (Clean & Colorful Cards)
# ==================================================
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

THEMES = {
    "Light": {
        "bg": "#F4F5F9",
        "bg_gradient": "#F4F5F9",
        "surface": "#FFFFFF",
        "surface_alpha": "rgba(255,255,255,0.9)",
        "border": "#E2E8F0",
        "text": "#1E293B",
        "subtitle": "#64748B",
        "primary": "#5B67CA",
        "accent": "#6366F1",
        "accent_soft": "rgba(99,102,241,0.1)",
        "sidebar_bg": "#4F46E5",
        "chart_bg": "rgba(0,0,0,0)",
        "chart_grid": "#F1F5F9",
        "chart_font": "#475569",
        "plotly_template": "plotly_white",
        "line_color": "#6366F1",
        "marker_color": "#EC4899",
        "area_color": "#818CF8",
        "bar_scale": [[0, "#C7D2FE"], [0.5, "#6366F1"], [1, "#4F46E5"]],
        "footer_bg": "#FFFFFF",
        "success": "#10B981",
        "danger": "#EF4444",
        "btn_bg": "#4F46E5",
        "btn_text": "#FFFFFF",
        "btn_border": "#4F46E5",
        "btn_hover_border": "#6366F1",
        "btn_hover_text": "#FFFFFF",
        "shadow": "0 4px 20px -2px rgba(0, 0, 0, 0.05)",
        "shadow_hover": "0 10px 25px -5px rgba(0, 0, 0, 0.1)",
    },
    "Dark": {
        "bg": "#0F172A",
        "bg_gradient": "#0F172A",
        "surface": "#1E293B",
        "surface_alpha": "rgba(30,41,59,0.9)",
        "border": "#334155",
        "text": "#F8FAFC",
        "subtitle": "#94A3B8",
        "primary": "#818CF8",
        "accent": "#818CF8",
        "accent_soft": "rgba(129,140,248,0.15)",
        "sidebar_bg": "#090D16",
        "chart_bg": "rgba(0,0,0,0)",
        "chart_grid": "#334155",
        "chart_font": "#94A3B8",
        "plotly_template": "plotly_dark",
        "line_color": "#818CF8",
        "marker_color": "#F472B6",
        "area_color": "#6366F1",
        "bar_scale": [[0, "#312E81"], [0.5, "#6366F1"], [1, "#818CF8"]],
        "footer_bg": "#1E293B",
        "success": "#34D399",
        "danger": "#F87171",
        "btn_bg": "#6366F1",
        "btn_text": "#FFFFFF",
        "btn_border": "#6366F1",
        "btn_hover_border": "#818CF8",
        "btn_hover_text": "#FFFFFF",
        "shadow": "0 4px 20px -2px rgba(0, 0, 0, 0.3)",
        "shadow_hover": "0 10px 25px -5px rgba(0, 0, 0, 0.4)",
    },
}

def apply_theme_css(t: dict):
    st.markdown(
        f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Kanit:wght@300;400;500;600&display=swap" rel="stylesheet">

    <style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{ background: transparent !important; }}

    html, body, p, span, div, label, h1, h2, h3, h4, h5, h6, button, input {{
        font-family: 'Plus Jakarta Sans', 'Kanit', sans-serif !important;
    }}

    .stApp {{ background: {t['bg']}; color: {t['text']}; }}

    /* ---------- Modern Sidebar Card Style ---------- */
    section[data-testid="stSidebar"] {{
        background-color: {t['sidebar_bg']} !important;
        border-right: 1px solid {t['border']};
        padding-top: 20px;
    }}
    section[data-testid="stSidebar"] * {{
        color: #FFFFFF !important;
    }}
    section[data-testid="stSidebar"] input, 
    section[data-testid="stSidebar"] select,
    section[data-testid="stSidebar"] div[data-baseweb="select"] * {{
        color: #1E293B !important;
    }}

    /* ---------- KPI Card Styles (คล้ายภาพตัวอย่าง) ---------- */
    .kpi-container {{
        display: flex;
        gap: 16px;
        width: 100%;
        margin-bottom: 20px;
    }}
    .kpi-box {{
        flex: 1;
        background: {t['surface']};
        border: 1px solid {t['border']};
        border-radius: 16px;
        padding: 20px;
        box-shadow: {t['shadow']};
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .kpi-box:hover {{
        transform: translateY(-3px);
        box-shadow: {t['shadow_hover']};
    }}
    .kpi-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }}
    .kpi-title {{
        font-size: 13px;
        font-weight: 600;
        color: {t['subtitle']};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .kpi-icon-badge {{
        width: 38px;
        height: 38px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .kpi-val {{
        font-size: 28px;
        font-weight: 700;
        color: {t['text']};
        letter-spacing: -0.5px;
        margin-bottom: 4px;
    }}
    .kpi-footer-text {{
        font-size: 12px;
        color: {t['subtitle']};
        font-weight: 500;
    }}

    /* ---------- Section Headers ---------- */
    .dashboard-card {{
        background: {t['surface']};
        border: 1px solid {t['border']};
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: {t['shadow']};
    }}

    /* ---------- Streamlit Plotly & Widget Overrides ---------- */
    div[data-testid="stPlotlyChart"] {{
        background: transparent;
        padding: 0px;
    }}

    div.stDownloadButton > button {{
        background-color: {t['btn_bg']} !important;
        color: {t['btn_text']} !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        box-shadow: {t['shadow']};
        width: 100%;
    }}
    div.stDownloadButton > button:hover {{
        opacity: 0.9;
        transform: translateY(-1px);
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )


def style_chart(fig, t: dict, height=350):
    fig.update_layout(
        template=t["plotly_template"],
        plot_bgcolor=t["chart_bg"],
        paper_bgcolor=t["chart_bg"],
        font=dict(color=t["chart_font"], family="Plus Jakarta Sans"),
        xaxis=dict(
            showgrid=False,
            zeroline=false,
            tickfont=dict(color=t["subtitle"], size=11),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=t["chart_grid"],
            zeroline=false,
            tickfont=dict(color=t["subtitle"], size=11),
        ),
        margin=dict(t=10, b=10, l=10, r=10),
        height=height,
        hoverlabel=dict(
            bgcolor=t["surface"], font_color=t["text"], font_family="Plus Jakarta Sans"
        ),
    )
    return fig


def render_kpi_card(title, value, subtitle, icon_name, bg_color, icon_color):
    return f"""
    <div class="kpi-box">
        <div class="kpi-header">
            <span class="kpi-title">{title}</span>
            <div class="kpi-icon-badge" style="background: {bg_color}; color: {icon_color};">
                {icon_svg(icon_name, 20)}
            </div>
        </div>
        <div class="kpi-val">{value}</div>
        <div class="kpi-footer-text">{subtitle}</div>
    </div>
    """


@st.cache_data(ttl=30)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip()
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
    return df


# ==================================================
# SIDEBAR CONTROLS
# ==================================================
with st.sidebar:
    st.markdown(
        "<h2 style='font-size: 20px; font-weight: 700; margin-bottom: 20px;'>📊 Dashboard UI</h2>",
        unsafe_allow_html=True,
    )

    theme_choice = st.radio(
        "Display Theme",
        options=["Light", "Dark"],
        index=0 if st.session_state.theme == "Light" else 1,
        horizontal=True,
    )
    st.session_state.theme = theme_choice
    theme = THEMES[theme_choice]

    st.markdown("---")
    refresh_seconds = st.selectbox(
        "Auto-refresh interval",
        options=[10, 30, 60, 120],
        index=1,
        format_func=lambda s: f"Every {s} seconds",
    )
    search_query = st.text_input("Search records", placeholder="Type to search...")

st_autorefresh(interval=refresh_seconds * 1000, key="auto_refresh")
apply_theme_css(theme)

# ==================================================
# MAIN CONTENT
# ==================================================
try:
    df = load_data()
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    room_col = None
    for c in ["room", "ห้อง", "ห้องเรียน", "classroom", "location", "สถานที่"]:
        if c in df.columns:
            room_col = c
            break

    with st.sidebar:
        if "Date" in df.columns and not df["Date"].isnull().all():
            min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
            date_range = st.date_input("Date range", [min_date, max_date])
            if len(date_range) == 2:
                df = df[(df["Date"] >= pd.to_datetime(date_range[0])) & (df["Date"] <= pd.to_datetime(date_range[1]))]

        if room_col:
            room_options = ["ทั้งหมด"] + sorted(df[room_col].dropna().unique().tolist())
            room_choice = st.selectbox("Filter Classroom", options=room_options)
            if room_choice != "ทั้งหมด":
                df = df[df[room_col] == room_choice]

        if search_query:
            df = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]

    # Top Header Banner
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
            <div>
                <h1 style="font-size: 26px; font-weight: 700; margin: 0; color: {theme['text']};">Overview Analytics</h1>
                <p style="font-size: 13px; color: {theme['subtitle']}; margin: 4px 0 0 0;">Real-time Classroom Occupancy & Activity Monitoring System</p>
            </div>
            <div style="background: {theme['surface']}; border: 1px solid {theme['border']}; padding: 8px 16px; border-radius: 12px; font-size: 12px; font-weight: 600;">
                🟢 Live Status: Connected
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty:
        st.warning("No records found matching your filters.")
        st.stop()

    # Calculate KPIs
    total_records = len(df)
    has_count = "Person Count" in df.columns and pd.api.types.is_numeric_dtype(df["Person Count"])
    total_people = int(df["Person Count"].sum()) if has_count else 0
    active_rooms = df[room_col].nunique() if room_col else 0

    peak_label = "—"
    if has_count and "Date" in df.columns:
        daily_peak = df.groupby("Date")["Person Count"].sum()
        if not daily_peak.empty:
            peak_val = int(daily_peak.max())
            peak_label = f"{peak_val:,}"

    # Render KPI Cards (จัดเรียง 4 กล่องสไตล์ Modern Dashboard เหมือนภาพตัวอย่าง)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(render_kpi_card("Total Records", f"{total_records:,}", "รายการทั้งหมด", "records", "rgba(99,102,241,0.12)", "#6366F1"), unsafe_allow_html=True)
    with col2:
        st.markdown(render_kpi_card("Total Occupancy", f"{total_people:,}", "ยอดสะสมรวม", "users", "rgba(16,185,129,0.12)", "#10B981"), unsafe_allow_html=True)
    with col3:
        st.markdown(render_kpi_card("Peak Traffic", peak_label, "ยอดสูงสุดต่อวัน", "peak", "rgba(244,63,94,0.12)", "#F43F5E"), unsafe_allow_html=True)
    with col4:
        st.markdown(render_kpi_card("Active Rooms", f"{active_rooms:,}", "ห้องที่มีการใช้งาน", "door", "rgba(245,158,11,0.12)", "#F59E0B"), unsafe_allow_html=True)

    # Charts Section
    if "Date" in df.columns and "Person Count" in df.columns:
        daily = df.groupby("Date")["Person Count"].sum().reset_index().sort_values("Date")

        st.markdown(f'<div class="dashboard-card"><h3 style="font-size: 16px; font-weight: 600; margin-bottom: 16px;">📈 แนวโน้มการเข้า-ออกห้องเรียนรายวัน</h3>', unsafe_allow_html=True)
        line_fig = px.line(
            daily, x="Date", y="Person Count", markers=True,
            color_discrete_sequence=[theme["line_color"]],
        )
        line_fig.update_traces(line=dict(width=3, shape="spline"), marker=dict(size=8, color=theme["marker_color"]))
        st.plotly_chart(style_chart(line_fig, theme, 320), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown(f'<div class="dashboard-card"><h3 style="font-size: 16px; font-weight: 600; margin-bottom: 16px;">📊 สัดส่วนการใช้งานรายวัน</h3>', unsafe_allow_html=True)
            bar_fig = px.bar(daily, x="Date", y="Person Count", color="Person Count", color_continuous_scale=theme["bar_scale"])
            bar_fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(style_chart(bar_fig, theme, 300), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            st.markdown(f'<div class="dashboard-card"><h3 style="font-size: 16px; font-weight: 600; margin-bottom: 16px;">🏫 ห้องเรียนยอดนิยม</h3>', unsafe_allow_html=True)
            if room_col:
                room_summary = df.groupby(room_col)["Person Count"].sum().reset_index().sort_values("Person Count", ascending=True).tail(5)
                room_fig = px.bar(room_summary, x="Person Count", y=room_col, orientation="h", color="Person Count", color_continuous_scale=theme["bar_scale"])
                room_fig.update_layout(coloraxis_showscale=False)
                st.plotly_chart(style_chart(room_fig, theme, 300), use_container_width=True)
            else:
                area_fig = px.area(daily, x="Date", y="Person Count", color_discrete_sequence=[theme["area_color"]])
                st.plotly_chart(style_chart(area_fig, theme, 300), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Download Report Section
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    col_dl1, col_dl2 = st.columns([3, 1])
    with col_dl1:
        st.markdown(f"<h4 style='font-size: 15px; margin: 0;'>📥 ส่งออกรายงานข้อมูล (CSV Report)</h4><p style='font-size: 12px; color: {theme['subtitle']}; margin: 4px 0 0 0;'>ดาวน์โหลดข้อมูลสถิติการใช้งานทั้งหมดตามเงื่อนไขตัวกรองปัจจุบัน</p>", unsafe_allow_html=True)
    with col_dl2:
        csv_data = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="Classroom_Analytics_Report.csv",
            mime="text/csv",
        )
    st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
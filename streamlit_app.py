from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image, ImageDraw, ImageOps
import streamlit as st
from streamlit_autorefresh import st_autorefresh


# =========================================================
# ICONS — Minimal line icons
# =========================================================
ICONS = {
    "records": """
        <rect x="5" y="3" width="14" height="18" rx="2"/>
        <path d="M8 8h8M8 12h8M8 16h5"/>
    """,

    "users": """
        <circle cx="9" cy="8" r="3"/>
        <path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/>
        <circle cx="17" cy="9" r="2.2"/>
        <path d="M15.5 14c2.5.5 4.2 2.7 4.2 5.5"/>
    """,

    "peak": """
        <path d="M3 18l5-6 4 3 6-8"/>
        <path d="M14 7h4v4"/>
    """,

    "rooms": """
        <path d="M4 21V5a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v16"/>
        <path d="M8 21v-4h8v4"/>
        <path d="M8 8h2M14 8h2M8 12h2M14 12h2"/>
    """,

    "activity": """
        <path d="M3 12h4l2-6 4 12 2-6h6"/>
    """,
}


def icon_svg(name: str, size: int = 20) -> str:
    body = ICONS.get(name, "")

    return (
        f'<svg width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="1.7" '
        f'stroke-linecap="round" stroke-linejoin="round">'
        f'{body}</svg>'
    )


# =========================================================
# FAVICON
# =========================================================
def make_circular_favicon(path: str, size: int = 256):

    p = Path(path)

    if not p.exists():
        return None

    img = Image.open(path).convert("RGBA")

    img = ImageOps.fit(
        img,
        (size, size),
        Image.LANCZOS,
        centering=(0.5, 0.5),
    )

    mask = Image.new("L", (size, size), 0)

    draw = ImageDraw.Draw(mask)

    draw.ellipse(
        (0, 0, size, size),
        fill=255,
    )

    img.putalpha(mask)

    return img


FAVICON_PATH = Path(_file_).parent / "favicon.png"

_favicon = (
    make_circular_favicon(str(FAVICON_PATH))
    if FAVICON_PATH.exists()
    else "●"
)


# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Classroom Occupancy Dashboard",
    page_icon=_favicon,
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# GOOGLE SHEETS
# =========================================================
SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "14FJt332r41O2JvookMlfzIqljBPSJ1wdt08XnnkTl-8/"
    "export?format=csv"
)


# =========================================================
# THEME
# =========================================================
if "theme" not in st.session_state:
    st.session_state.theme = "Light"


THEMES = {

    "Light": {

        "bg": "#F5F7FB",

        "surface": "#FFFFFF",

        "text": "#182230",

        "muted": "#7A8494",

        "border": "#E9ECF2",

        "sidebar": "#FFFFFF",

        "sidebar_text": "#202938",

        "grid": "#E9EDF4",

        "purple": "#7C4DFF",

        "blue": "#3182F6",

        "red": "#F45B69",

        "orange": "#FF9F43",

    },

    "Dark": {

        "bg": "#0D111C",

        "surface": "#151B2A",

        "text": "#F4F6FA",

        "muted": "#9AA5B8",

        "border": "#252D40",

        "sidebar": "#111725",

        "sidebar_text": "#F4F6FA",

        "grid": "#252D40",

        "purple": "#9A7BFF",

        "blue": "#4E9BFF",

        "red": "#FF7180",

        "orange": "#FFAE5C",

    },
}


theme = THEMES[st.session_state.theme]


# =========================================================
# CSS
# =========================================================
def apply_css(t):

    st.markdown(
        f"""

<style>

@import url(
'https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600;700&display=swap'
);


/* =====================================================
   GLOBAL
===================================================== */

html,
body,
[class*="css"] {{

    font-family: 'Kanit', sans-serif !important;

}}

.stApp {{

    background: {t["bg"]};

    color: {t["text"]};

}}

.main .block-container {{

    max-width: 1500px;

    padding:
        28px
        38px
        42px
        38px;

}}

#MainMenu {{

    visibility: hidden;

}}

footer {{

    visibility: hidden;

}}

header[data-testid="stHeader"] {{

    background: transparent !important;

}}


/* =====================================================
   SIDEBAR
===================================================== */

section[data-testid="stSidebar"] {{

    background: {t["sidebar"]};

    border-right:
        1px solid
        {t["border"]};

}}

section[data-testid="stSidebar"] > div {{

    padding:
        24px
        18px;

}}

section[data-testid="stSidebar"] * {{

    font-family:
        'Kanit',
        sans-serif !important;

}}

.side-logo {{

    display:
        flex;

    align-items:
        center;

    gap:
        12px;

    margin-bottom:
        26px;

}}

.side-logo-box {{

    width:
        42px;

    height:
        42px;

    border-radius:
        12px;

    background:
        linear-gradient(
            135deg,
            #7C4DFF,
            #5B35D5
        );

    color:
        white;

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    font-size:
        21px;

    font-weight:
        700;

    box-shadow:
        0 8px 20px
        rgba(124,77,255,.20);

}}

.side-logo-title {{

    color:
        {t["sidebar_text"]};

    font-size:
        16px;

    font-weight:
        600;

    line-height:
        1.15;

}}

.side-logo-sub {{

    color:
        {t["muted"]};

    font-size:
        10px;

    margin-top:
        3px;

}}

.side-section {{

    color:
        {t["muted"]};

    font-size:
        10px;

    text-transform:
        uppercase;

    letter-spacing:
        .12em;

    margin:
        22px 0 8px;

}}

.side-info {{

    background:
        {t["bg"]};

    border:
        1px solid
        {t["border"]};

    border-radius:
        12px;

    padding:
        13px;

    margin-top:
        8px;

}}

.side-info-title {{

    color:
        {t["text"]};

    font-size:
        12px;

    font-weight:
        500;

    margin-bottom:
        5px;

}}

.side-info-text {{

    color:
        {t["muted"]};

    font-size:
        11px;

    line-height:
        1.6;

}}

section[data-testid="stSidebar"] label {{

    color:
        {t["text"]}
        !important;

}}

section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"]
div[data-baseweb="select"] > div {{

    background:
        {t["surface"]}
        !important;

    color:
        {t["text"]}
        !important;

    border:
        1px solid
        {t["border"]}
        !important;

    border-radius:
        9px
        !important;

}}


/* =====================================================
   HEADER
===================================================== */

.topbar {{

    display:
        flex;

    align-items:
        center;

    justify-content:
        space-between;

    margin-bottom:
        24px;

}}

.welcome {{

    font-size:
        27px;

    font-weight:
        600;

    color:
        {t["text"]};

    line-height:
        1.25;

}}

.welcome-sub {{

    color:
        {t["muted"]};

    font-size:
        12px;

    margin-top:
        4px;

}}

.online-pill {{

    display:
        inline-flex;

    align-items:
        center;

    gap:
        8px;

    padding:
        8px 14px;

    border-radius:
        30px;

    background:
        {t["surface"]};

    border:
        1px solid
        {t["border"]};

    color:
        {t["text"]};

    font-size:
        11px;

    box-shadow:
        0 4px 15px
        rgba(20,30,50,.05);

}}

.online-dot {{

    width:
        7px;

    height:
        7px;

    border-radius:
        50%;

    background:
        #22C55E;

    box-shadow:
        0 0 0 4px
        rgba(34,197,94,.12);

}}


/* =====================================================
   KPI
===================================================== */

.kpi {{

    position:
        relative;

    min-height:
        148px;

    padding:
        22px;

    border-radius:
        18px;

    color:
        white;

    overflow:
        hidden;

    box-shadow:
        0 10px 28px
        rgba(30,40,70,.10);

    transition:
        .2s ease;

}}

.kpi:hover {{

    transform:
        translateY(-2px);

    box-shadow:
        0 14px 32px
        rgba(30,40,70,.15);

}}

.kpi::after {{

    content:
        "";

    position:
        absolute;

    width:
        120px;

    height:
        120px;

    border-radius:
        50%;

    right:
        -38px;

    top:
        -45px;

    background:
        rgba(255,255,255,.10);

}}

.kpi-purple {{

    background:
        linear-gradient(
            135deg,
            #8055F7 0%,
            #9D73F5 100%
        );

}}

.kpi-blue {{

    background:
        linear-gradient(
            135deg,
            #2F73E8 0%,
            #4A9AF5 100%
        );

}}

.kpi-red {{

    background:
        linear-gradient(
            135deg,
            #EF626E 0%,
            #F48B8F 100%
        );

}}

.kpi-orange {{

    background:
        linear-gradient(
            135deg,
            #F39A3D 0%,
            #FFB35F 100%
        );

}}

.kpi-head {{

    display:
        flex;

    justify-content:
        space-between;

    align-items:
        center;

}}

.kpi-label {{

    font-size:
        12px;

    opacity:
        .9;

    font-weight:
        400;

}}

.kpi-icon {{

    width:
        34px;

    height:
        34px;

    border-radius:
        10px;

    background:
        rgba(255,255,255,.16);

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

}}

.kpi-value {{

    margin-top:
        17px;

    font-size:
        30px;

    line-height:
        1;

    font-weight:
        600;

    letter-spacing:
        -.5px;

}}

.kpi-sub {{

    margin-top:
        9px;

    font-size:
        10.5px;

    opacity:
        .82;

}}


/* =====================================================
   STATUS
===================================================== */

.status-bar {{

    display:
        flex;

    align-items:
        center;

    gap:
        10px;

    margin:
        20px 0;

    color:
        {t["muted"]};

    font-size:
        11px;

}}

.status-line {{

    width:
        1px;

    height:
        13px;

    background:
        {t["border"]};

}}


/* =====================================================
   CHART
===================================================== */

.chart-title {{

    color:
        {t["text"]};

    font-size:
        16px;

    font-weight:
        600;

    margin-bottom:
        2px;

}}

.chart-sub {{

    color:
        {t["muted"]};

    font-size:
        10.5px;

    margin-bottom:
        8px;

}}

div[data-testid="stPlotlyChart"] {{

    background:
        {t["surface"]};

    border:
        1px solid
        {t["border"]};

    border-radius:
        16px;

    padding:
        8px 12px;

    box-shadow:
        0 5px 20px
        rgba(30,40,70,.045);

}}


/* =====================================================
   DOWNLOAD
===================================================== */

div.stDownloadButton > button {{

    width:
        100%;

    border-radius:
        10px
        !important;

    border:
        1px solid
        {t["border"]}
        !important;

    background:
        {t["surface"]}
        !important;

    color:
        {t["text"]}
        !important;

    font-family:
        'Kanit',
        sans-serif
        !important;

}}

div.stDownloadButton > button:hover {{

    border-color:
        {t["purple"]}
        !important;

    color:
        {t["purple"]}
        !important;

}}


/* =====================================================
   FOOTER
===================================================== */

.footer {{

    text-align:
        center;

    color:
        {t["muted"]};

    font-size:
        10px;

    margin-top:
        32px;

    padding-top:
        18px;

    border-top:
        1px solid
        {t["border"]};

}}


/* =====================================================
   MOBILE
===================================================== */

@media (max-width: 900px) {{

    .main .block-container {{

        padding:
            20px 16px;

    }}

    .welcome {{

        font-size:
            22px;

    }}

    .kpi {{

        min-height:
            125px;

    }}

}}

</style>
        """,
        unsafe_allow_html=True,
    )


apply_css(theme)


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:

    st.markdown(
        """
        <div class="side-logo">

            <div class="side-logo-box">
                S
            </div>

            <div>

                <div class="side-logo-title">
                    SMARTZONE
                </div>

                <div class="side-logo-sub">
                    OCCUPANCY MONITORING
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        '<div class="side-section">Dashboard</div>',
        unsafe_allow_html=True,
    )


    theme_choice = st.radio(
        "Theme",
        ["Light", "Dark"],
        index=(
            0
            if st.session_state.theme == "Light"
            else 1
        ),
        horizontal=True,
    )

    st.session_state.theme = theme_choice


    st.markdown(
        '<div class="side-section">Auto Refresh</div>',
        unsafe_allow_html=True,
    )


    refresh_seconds = st.selectbox(
        "Refresh",
        [10, 30, 60, 120],
        index=1,
        format_func=lambda x:
            f"Every {x} seconds",
        label_visibility="collapsed",
    )


    st.markdown(
        '<div class="side-section">Search</div>',
        unsafe_allow_html=True,
    )


    search_query = st.text_input(
        "Search",
        placeholder="Search records...",
        label_visibility="collapsed",
    )


    st.markdown(
        '<div class="side-section">Information</div>',
        unsafe_allow_html=True,
    )


    st.markdown(
        """
        <div class="side-info">

            <div class="side-info-title">
                Data Source
            </div>

            <div class="side-info-text">

                Google Sheets<br>

                Real-Time Occupancy Data

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


st_autorefresh(
    interval=refresh_seconds * 1000,
    key="dashboard_refresh",
)


# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data(ttl=30)
def load_data():

    df = pd.read_csv(SHEET_URL)

    df.columns = (
        df.columns
        .str.strip()
    )


    if "Date" in df.columns:

        df["Date"] = pd.to_datetime(
            df["Date"],
            errors="coerce",
        )


    if "Person Count" in df.columns:

        df["Person Count"] = pd.to_numeric(
            df["Person Count"],
            errors="coerce",
        ).fillna(0)


    return df


# =========================================================
# FIND COLUMN
# =========================================================
def find_column(df, candidates):

    for col in df.columns:

        col_lower = str(col).lower()

        for candidate in candidates:

            if candidate.lower() in col_lower:

                return col

    return None


# =========================================================
# MAIN
# =========================================================
try:

    df = load_data()


    # -----------------------------------------------------
    # FIND COLUMNS
    # -----------------------------------------------------

    room_col = find_column(
        df,
        [
            "room",
            "ห้อง",
            "ห้องเรียน",
            "classroom",
            "location",
            "สถานที่",
        ],
    )


    status_col = find_column(
        df,
        [
            "status",
            "สถานะ",
        ],
    )


    # =====================================================
    # SIDEBAR FILTER
    # =====================================================

    with st.sidebar:


        if (
            "Date" in df.columns
            and not df["Date"].dropna().empty
        ):

            min_date = (
                df["Date"]
                .min()
                .date()
            )

            max_date = (
                df["Date"]
                .max()
                .date()
            )


            st.markdown(
                '<div class="side-section">'
                'Date Range'
                '</div>',
                unsafe_allow_html=True,
            )


            date_range = st.date_input(
                "Date Range",

                value=(
                    min_date,
                    max_date,
                ),

                min_value=min_date,

                max_value=max_date,

                label_visibility="collapsed",
            )


            if (
                isinstance(date_range, tuple)
                and len(date_range) == 2
            ):

                df = df[
                    (
                        df["Date"]
                        >= pd.Timestamp(
                            date_range[0]
                        )
                    )
                    &
                    (
                        df["Date"]
                        <
                        pd.Timestamp(
                            date_range[1]
                        )
                        + pd.Timedelta(days=1)
                    )
                ]


        if room_col:

            st.markdown(
                '<div class="side-section">'
                'Classroom'
                '</div>',
                unsafe_allow_html=True,
            )


            room_options = (
                ["ทั้งหมด"]
                +
                sorted(
                    df[room_col]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )
            )


            room_choice = st.selectbox(
                "Classroom",

                room_options,

                label_visibility="collapsed",
            )


            if room_choice != "ทั้งหมด":

                df = df[
                    df[room_col]
                    .astype(str)
                    == room_choice
                ]


        if search_query:

            mask = (
                df.astype(str)
                .apply(
                    lambda col:
                    col.str.contains(
                        search_query,
                        case=False,
                        na=False,
                    )
                )
                .any(axis=1)
            )

            df = df[mask]


        st.markdown(
            f"""
            <div class="side-info">

                <div class="side-info-title">
                    System Status
                </div>

                <div class="side-info-text">

                    <span style="color:#22C55E;">
                    ● Online
                    </span>
                    <br>

                    Records:
                    {len(df):,}
                    <br>

                    Sync:
                    {datetime.now().strftime("%H:%M:%S")}

                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    # =====================================================
    # EMPTY
    # =====================================================

    if df.empty:

        st.warning(
            "ไม่พบข้อมูลตามเงื่อนไขที่เลือก "
            "กรุณาปรับช่วงวันที่ ห้องเรียน "
            "หรือคำค้นหา"
        )

        st.stop()


    # =====================================================
    # HEADER
    # =====================================================

    st.markdown(
        f"""
        <div class="topbar">

            <div>

                <div class="welcome">
                    Dashboard
                </div>

                <div class="welcome-sub">
                    Classroom Occupancy
                    & Analytics Monitoring
                </div>

            </div>


            <div class="online-pill">

                <span class="online-dot"></span>

                SYSTEM ONLINE

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # =====================================================
    # KPI CALCULATION
    # =====================================================

    total_records = len(df)


    has_count = (
        "Person Count" in df.columns
        and
        pd.api.types.is_numeric_dtype(
            df["Person Count"]
        )
    )


    total_people = (

        int(
            df["Person Count"].sum()
        )

        if has_count

        else 0
    )


    average_people = (

        round(
            float(
                df["Person Count"].mean()
            ),
            1,
        )

        if has_count
        and not df.empty

        else 0
    )


    peak_value = 0

    peak_date_text = "-"


    if (
        has_count
        and "Date" in df.columns
    ):

        daily_sum = (

            df.assign(
                DateOnly=df["Date"].dt.date
            )

            .groupby(
                "DateOnly"
            )["Person Count"]

            .sum()

            .sort_values(
                ascending=False
            )
        )


        if not daily_sum.empty:

            peak_value = int(
                daily_sum.iloc[0]
            )


            peak_date_text = (
                pd.to_datetime(
                    daily_sum.index[0]
                )
                .strftime(
                    "%d/%m/%Y"
                )
            )


    active_rooms = (

        df[room_col].nunique()

        if room_col

        else 0
    )


    # =====================================================
    # KPI CARDS
    # =====================================================

    c1, c2, c3, c4 = st.columns(
        4,
        gap="medium",
    )


    with c1:

        st.markdown(
            f"""
            <div class="kpi kpi-purple">

                <div class="kpi-head">

                    <div class="kpi-label">
                        Total Records
                    </div>

                    <div class="kpi-icon">
                        {icon_svg("records", 18)}
                    </div>

                </div>


                <div class="kpi-value">
                    {total_records:,}
                </div>


                <div class="kpi-sub">
                    ข้อมูลทั้งหมดที่บันทึก
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    with c2:

        st.markdown(
            f"""
            <div class="kpi kpi-blue">

                <div class="kpi-head">

                    <div class="kpi-label">
                        Total Occupancy
                    </div>

                    <div class="kpi-icon">
                        {icon_svg("users", 18)}
                    </div>

                </div>


                <div class="kpi-value">
                    {total_people:,}
                </div>


                <div class="kpi-sub">
                    จำนวนบุคคลสะสมที่ตรวจพบ
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    with c3:

        st.markdown(
            f"""
            <div class="kpi kpi-red">

                <div class="kpi-head">

                    <div class="kpi-label">
                        Peak Day
                    </div>

                    <div class="kpi-icon">
                        {icon_svg("peak", 18)}
                    </div>

                </div>


                <div class="kpi-value">
                    {peak_value:,}
                </div>


                <div class="kpi-sub">
                    วันที่ {peak_date_text}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    with c4:

        st.markdown(
            f"""
            <div class="kpi kpi-orange">

                <div class="kpi-head">

                    <div class="kpi-label">
                        Active Classrooms
                    </div>

                    <div class="kpi-icon">
                        {icon_svg("rooms", 18)}
                    </div>

                </div>


                <div class="kpi-value">
                    {active_rooms:,}
                </div>


                <div class="kpi-sub">
                    ห้องเรียนที่มีข้อมูลการใช้งาน
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


    # =====================================================
    # STATUS BAR
    # =====================================================

    st.markdown(
        f"""
        <div class="status-bar">

            <span style="color:#22C55E;">
                ● Live Data
            </span>

            <span class="status-line"></span>

            <span>
                Google Sheets
            </span>

            <span class="status-line"></span>

            <span>
                Average Occupancy:
                {average_people} คน
            </span>

            <span class="status-line"></span>

            <span>
                Last sync:
                {datetime.now().strftime(
                    "%d/%m/%Y %H:%M:%S"
                )}
            </span>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # =====================================================
    # DAILY TREND
    # =====================================================

    if (
        "Date" in df.columns
        and has_count
    ):

        daily = (

            df.assign(
                DateOnly=df["Date"].dt.date
            )

            .groupby(
                "DateOnly",
                as_index=False
            )["Person Count"]

            .sum()

            .sort_values(
                "DateOnly"
            )
        )


        st.markdown(
            """
            <div class="chart-title">
                Occupancy Overview
            </div>

            <div class="chart-sub">
                จำนวนบุคคลที่ตรวจพบรายวัน
            </div>
            """,
            unsafe_allow_html=True,
        )


        line_fig = px.line(
            daily,

            x="DateOnly",

            y="Person Count",

            markers=True,
        )


        line_fig.update_traces(

            line=dict(
                color=theme["purple"],
                width=3,
                shape="spline",
            ),

            marker=dict(
                color=theme["purple"],
                size=7,
                line=dict(
                    width=2,
                    color="white",
                ),
            ),

            fill="tozeroy",

            fillcolor=(
                "rgba(124,77,255,0.10)"
            ),

            hovertemplate=(
                "วันที่ %{x|%d/%m/%Y}"
                "<br>"
                "จำนวนคน: %{y:,} คน"
                "<extra></extra>"
            ),
        )


        line_fig.update_layout(

            height=350,

            margin=dict(
                l=10,
                r=10,
                t=10,
                b=10,
            ),

            plot_bgcolor=
                "rgba(0,0,0,0)",

            paper_bgcolor=
                "rgba(0,0,0,0)",

            font=dict(
                family="Kanit",
                color=theme["text"],
            ),

            xaxis=dict(
                title="",
                showgrid=False,
                tickfont=dict(
                    color=theme["muted"]
                ),
            ),

            yaxis=dict(
                title="จำนวนคน",
                showgrid=True,
                gridcolor=theme["grid"],
                zeroline=False,
                tickfont=dict(
                    color=theme["muted"]
                ),
            ),

            hoverlabel=dict(
                bgcolor=theme["surface"],
                font_family="Kanit",
            ),

            showlegend=False,
        )


        st.plotly_chart(
            line_fig,

            use_container_width=True,

            config={
                "displayModeBar": False
            },
        )


        # =================================================
        # TWO CHARTS
        # =================================================

        col_a, col_b = st.columns(
            2,
            gap="large",
        )


        # =================================================
        # ROOM STATUS
        # =================================================

        with col_a:

            st.markdown(
                """
                <div class="chart-title">
                    Room Status
                </div>

                <div class="chart-sub">
                    สัดส่วนสถานะการใช้งานห้องเรียน
                </div>
                """,
                unsafe_allow_html=True,
            )


            if status_col:

                status_data = (

                    df[status_col]

                    .fillna("ไม่ระบุ")

                    .astype(str)

                    .value_counts()

                    .reset_index()
                )


                status_data.columns = [
                    "Status",
                    "Count",
                ]


            else:

                status_data = pd.DataFrame(
                    {
                        "Status": [
                            "มีคนอยู่",
                            "ไม่มีคนอยู่",
                        ],

                        "Count": [

                            int(
                                (
                                    df["Person Count"]
                                    > 0
                                ).sum()
                            ),

                            int(
                                (
                                    df["Person Count"]
                                    == 0
                                ).sum()
                            ),

                        ],
                    }
                )


            donut = go.Figure(

                data=[

                    go.Pie(

                        labels=
                            status_data["Status"],

                        values=
                            status_data["Count"],

                        hole=0.68,

                        textinfo="percent",

                        textfont=dict(
                            family="Kanit",
                            size=12,
                        ),

                        marker=dict(
                            colors=[
                                theme["purple"],
                                theme["orange"],
                                theme["blue"],
                                theme["red"],
                            ]
                        ),

                        hovertemplate=(
                            "%{label}"
                            "<br>"
                            "%{value:,} รายการ"
                            "<br>"
                            "%{percent}"
                            "<extra></extra>"
                        ),
                    )
                ]
            )


            donut.update_layout(

                height=350,

                margin=dict(
                    l=10,
                    r=10,
                    t=10,
                    b=10,
                ),

                paper_bgcolor=
                    "rgba(0,0,0,0)",

                plot_bgcolor=
                    "rgba(0,0,0,0)",

                font=dict(
                    family="Kanit",
                    color=theme["text"],
                ),

                legend=dict(

                    orientation="h",

                    yanchor="bottom",

                    y=-0.04,

                    xanchor="center",

                    x=0.5,

                    font=dict(
                        family="Kanit",
                        size=10,
                        color=theme["muted"],
                    ),
                ),

                showlegend=True,
            )


            st.plotly_chart(
                donut,

                use_container_width=True,

                config={
                    "displayModeBar": False
                },
            )


        # =================================================
        # TOP CLASSROOMS
        # =================================================

        with col_b:

            st.markdown(
                """
                <div class="chart-title">
                    Top Classrooms
                </div>

                <div class="chart-sub">
                    ห้องเรียนที่มีจำนวนผู้ใช้งานสะสมสูงสุด
                </div>
                """,
                unsafe_allow_html=True,
            )


            if room_col:

                room_summary = (

                    df.groupby(
                        room_col
                    )["Person Count"]

                    .sum()

                    .reset_index()

                    .sort_values(
                        "Person Count",
                        ascending=True,
                    )

                    .tail(5)
                )


                room_fig = px.bar(

                    room_summary,

                    x="Person Count",

                    y=room_col,

                    orientation="h",
                )


                room_fig.update_traces(

                    marker=dict(
                        color=theme["blue"],
                        line=dict(
                            width=0
                        ),
                    ),

                    hovertemplate=(
                        "ห้อง %{y}"
                        "<br>"
                        "จำนวนคน: %{x:,}"
                        "<extra></extra>"
                    ),
                )


                room_fig.update_layout(

                    height=350,

                    margin=dict(
                        l=10,
                        r=10,
                        t=10,
                        b=10,
                    ),

                    plot_bgcolor=
                        "rgba(0,0,0,0)",

                    paper_bgcolor=
                        "rgba(0,0,0,0)",

                    font=dict(
                        family="Kanit",
                        color=theme["text"],
                    ),

                    xaxis=dict(
                        title="จำนวนคนสะสม",
                        showgrid=True,
                        gridcolor=theme["grid"],
                        zeroline=False,
                        tickfont=dict(
                            color=theme["muted"]
                        ),
                    ),

                    yaxis=dict(
                        title="",
                        showgrid=False,
                        tickfont=dict(
                            color=theme["text"]
                        ),
                    ),

                    showlegend=False,
                )


                st.plotly_chart(

                    room_fig,

                    use_container_width=True,

                    config={
                        "displayModeBar": False
                    },
                )


            else:

                st.info(
                    "ไม่พบคอลัมน์ห้องเรียน "
                    "ใน Google Sheets"
                )


    # =====================================================
    # DOWNLOAD
    # =====================================================

    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )


    d1, d2 = st.columns(
        [1, 3]
    )


    with d1:

        csv_data = (
            df
            .to_csv(
                index=False
            )
            .encode(
                "utf-8-sig"
            )
        )


        st.download_button(

            label=
                "Download Report (.CSV)",

            data=csv_data,

            file_name=
                "Classroom_Monitoring_Report.csv",

            mime=
                "text/csv",
        )


    # =====================================================
    # FOOTER
    # =====================================================

    st.markdown(
        """
        <div class="footer">

            SMARTZONE ·
            Classroom Occupancy
            & Analytics Dashboard

            <br>

            Prince of Songkla University ·
            Academic Project 2026

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# ERROR
# =========================================================

except Exception as e:

    st.error(
        "ไม่สามารถโหลดข้อมูลจาก Google Sheets ได้"
    )

    st.code(
        str(e),
        language="text",
    )
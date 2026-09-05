import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

from hr_generator.config import TRANSLATIONS, LANGUAGE_DATA, MIN_EMPLOYEES, MAX_EMPLOYEES, DEFAULT_EMPLOYEES
from hr_generator.models import GeneratorConfig
from hr_generator.generator import generate_dataset


# ── Design tokens ────────────────────────────────────────────────────────────
# Apple-inspired system palette: one accent, a neutral grey scale, hairlines.
BLUE       = "#0071e3"              # accent / interactive
BLUE_HOVER = "#0077ed"
BLUE_TINT  = "rgba(0, 113, 227, 0.10)"
INK        = "#1d1d1f"              # primary label
INK_2      = "#6e6e73"              # secondary label
INK_3      = "#86868b"              # tertiary label
SURFACE    = "#ffffff"              # cards
CANVAS     = "#fbfbfd"              # page
GROUPED    = "#f5f5f7"              # grouped background / fills
HAIRLINE   = "#d2d2d7"              # separators
HAIRLINE_L = "rgba(0, 0, 0, 0.07)"  # card borders
GREEN      = "#34c759"
TEAL       = "#30b0c7"
INDIGO     = "#5856d6"
ORANGE     = "#ff9500"

FONT = ('-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", '
        '"Helvetica Neue", Inter, "Hiragino Sans", "Hiragino Kaku Gothic ProN", '
        '"Yu Gothic", Meiryo, sans-serif')
PLOT_FONT = "-apple-system, BlinkMacSystemFont, Inter, Helvetica Neue, sans-serif"
CHART_COLORS = [BLUE, TEAL, INDIGO, "#5ac8fa", GREEN, ORANGE]
CHART_H = 340
# ─────────────────────────────────────────────────────────────────────────────


def setup_page():
    st.set_page_config(
        page_title="HR Data Generator",
        page_icon="👥",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


def inject_css():
    st.markdown(f"""
    <style>
    /* Inter stands in for SF Pro on non-Apple platforms. */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ── Base ── */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {CANVAS} !important;
        color: {INK};
        font-family: {FONT};
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }}
    [data-testid="stAppViewContainer"] > .main > .block-container {{
        padding: 1.2rem 2rem 5rem;
        max-width: 1120px;
    }}
    p, li, div, span, label, td, th {{ font-family: {FONT}; }}

    /* ── Hide Streamlit chrome + reclaim the sidebar gutter ── */
    #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stSidebar"], [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"] {{ display: none !important; }}
    section[data-testid="stMain"] {{ margin-left: 0 !important; padding-left: 0 !important; }}

    /* ── Typography ── */
    h1, h2, h3, h4, h5 {{
        color: {INK} !important;
        font-family: {FONT} !important;
        font-weight: 600 !important;
        letter-spacing: -0.022em;
    }}

    /* ── Reusable surfaces ── */
    .ad-nav {{
        display: flex; align-items: center; gap: 10px;
        padding: 0.1rem 0 0.9rem;
    }}
    .ad-mark {{
        width: 30px; height: 30px; border-radius: 8px; flex-shrink: 0;
        background: {INK}; color: #fff;
        display: flex; align-items: center; justify-content: center;
    }}
    .ad-wordmark {{
        font-size: 0.95rem; font-weight: 600; letter-spacing: -0.015em; color: {INK};
    }}
    .ad-hero {{ text-align: center; padding: 1.2rem 0 2rem; }}
    .ad-hero h1 {{
        font-size: 2.6rem; line-height: 1.08; font-weight: 600;
        letter-spacing: -0.03em; margin: 0 0 0.55rem;
    }}
    .ad-hero p {{
        font-size: 1.1rem; line-height: 1.45; color: {INK_2};
        margin: 0 auto; max-width: 34rem; font-weight: 400;
    }}
    .ad-rule {{ height: 1px; background: {HAIRLINE}; opacity: 0.7; margin: 0 0 1.8rem; }}

    .ad-card {{
        background: {SURFACE}; border: 1px solid {HAIRLINE_L};
        border-radius: 18px; padding: 1.5rem 1.6rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .ad-section {{
        font-size: 0.78rem; font-weight: 600; color: {INK_3};
        letter-spacing: 0.01em; margin: 0 0 0.35rem;
    }}
    [class*="st-key-adgroup"] {{
        background: {SURFACE} !important;
        border: 1px solid {HAIRLINE_L} !important;
        border-radius: 14px !important;
        padding: 0.45rem 1rem 0.6rem !important;
        margin-bottom: 1.15rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .ad-row {{
        display: flex; align-items: baseline; justify-content: space-between;
        padding: 0.5rem 0 0.15rem; gap: 12px;
    }}
    .ad-row + .ad-row {{ border-top: 1px solid {HAIRLINE_L}; }}
    .ad-label {{ font-size: 0.9rem; color: {INK}; font-weight: 400; }}
    .ad-value {{ font-size: 0.9rem; color: {INK_2}; font-weight: 500;
                 font-variant-numeric: tabular-nums; white-space: nowrap; }}

    [class*="st-key-adchart"] {{
        background: {SURFACE} !important;
        border: 1px solid {HAIRLINE_L} !important;
        border-radius: 16px !important;
        padding: 0.4rem 0.35rem 0.2rem !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}

    .ad-stat {{
        background: {SURFACE}; border: 1px solid {HAIRLINE_L}; border-radius: 16px;
        padding: 1.05rem 1.2rem; flex: 1; min-width: 132px;
    }}
    .ad-stat-value {{ font-size: 1.9rem; font-weight: 600; letter-spacing: -0.028em;
                      line-height: 1.05; font-variant-numeric: tabular-nums; }}
    .ad-stat-label {{ font-size: 0.78rem; color: {INK_2}; margin-top: 6px; }}

    .ad-pill {{
        display: inline-flex; align-items: center; gap: 6px;
        background: {GROUPED}; border-radius: 980px;
        padding: 5px 12px; font-size: 0.78rem; margin: 0 6px 6px 0;
    }}
    .ad-pill .k {{ color: {INK_3}; }}
    .ad-pill .v {{ color: {INK}; font-weight: 500; font-variant-numeric: tabular-nums; }}

    .ad-empty {{
        background: {SURFACE}; border: 1px solid {HAIRLINE_L}; border-radius: 18px;
        padding: 3.2rem 2rem; text-align: center;
    }}
    .ad-empty h3 {{ font-size: 1.12rem; margin: 0.9rem 0 0.35rem; font-weight: 600; }}
    .ad-empty p {{ font-size: 0.9rem; color: {INK_2}; margin: 0 auto; max-width: 24rem;
                   line-height: 1.5; }}

    .ad-note {{ font-size: 0.82rem; color: {INK_2}; margin: 0.7rem 0 1.1rem; }}
    .ad-foot {{ font-size: 0.78rem; color: {INK_3}; line-height: 1.9; margin-top: 1.6rem; }}
    .ad-foot a {{ color: {INK_3}; text-decoration: none; }}
    .ad-foot a:hover {{ color: {BLUE}; }}

    /* ── Field reference table ── */
    .ad-table {{ width: 100%; border-collapse: collapse; }}
    .ad-table th {{
        text-align: left; padding: 6px 12px 10px; font-size: 0.76rem;
        font-weight: 600; color: {INK_3}; border-bottom: 1px solid {HAIRLINE};
    }}
    .ad-table td {{ padding: 9px 12px; font-size: 0.85rem; vertical-align: top; }}
    .ad-table tr td:first-child {{ color: {INK}; font-weight: 500; white-space: nowrap; }}
    .ad-table tr td:last-child {{ color: {INK_2}; }}
    .ad-table tbody tr + tr td {{ border-top: 1px solid {HAIRLINE_L}; }}

    /* ── Select ── */
    [data-testid="stSelectbox"] div[role="group"] {{
        background-color: {SURFACE} !important;
        border: 1px solid {HAIRLINE} !important;
        border-radius: 10px !important;
        min-height: 38px;
        transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }}
    [data-testid="stSelectbox"] div[role="group"]:hover {{ border-color: {INK_3} !important; }}
    [data-testid="stSelectbox"] div[role="group"]:focus-within {{
        border-color: {BLUE} !important;
        box-shadow: 0 0 0 3.5px {BLUE_TINT} !important;
    }}
    [data-testid="stSelectbox"] input {{
        color: {INK} !important; font-size: 0.88rem !important; font-family: {FONT} !important;
    }}
    [role="listbox"] {{
        background-color: {SURFACE} !important;
        border-radius: 12px !important;
        border: 1px solid {HAIRLINE_L} !important;
        box-shadow: 0 12px 32px rgba(0,0,0,0.12) !important;
        padding: 4px !important;
    }}
    [role="option"] {{
        font-size: 0.88rem !important; border-radius: 8px !important; color: {INK} !important;
    }}
    [role="option"]:hover, [role="option"][data-selected="true"] {{
        background-color: {GROUPED} !important;
    }}

    /* ── Slider ──
       The value bubble and tick numbers are redundant: the row above each
       slider states the value, so the control itself stays quiet. */
    [data-testid="stSliderThumbValue"], [data-testid="stSliderTickBar"] {{
        display: none !important;
    }}
    [data-testid="stSlider"] {{ padding: 0 0 0.3rem; }}
    /* Widgets inside a grouped card sit closer together than page-level ones. */
    [class*="st-key-adgroup"] [data-testid="stVerticalBlock"] {{ gap: 0.1rem !important; }}
    /* stSlider > group > track > thumb (the track's only data-rac child) */
    [data-testid="stSlider"] > div > div > div[data-rac] {{
        background: #ffffff !important;
        border: 0.5px solid rgba(0,0,0,0.05) !important;
        box-shadow: 0 3px 8px rgba(0,0,0,0.15), 0 1px 1px rgba(0,0,0,0.16) !important;
        height: 21px !important; width: 21px !important;
    }}

    /* ── Toggle / checkbox ── */
    [data-testid="stCheckbox"] label, [data-testid="stWidgetLabel"] p {{
        color: {INK} !important; font-size: 0.9rem !important;
    }}

    /* ── Primary button (Apple pill) ── */
    [data-testid="stBaseButton-primary"] {{
        background: {BLUE} !important;
        border: none !important;
        border-radius: 980px !important;
        color: #fff !important;
        font-weight: 500 !important;
        font-size: 0.94rem !important;
        letter-spacing: -0.01em;
        padding: 0.68rem 1.5rem !important;
        box-shadow: none !important;
        transition: background 0.18s ease, transform 0.12s ease;
    }}
    [data-testid="stBaseButton-primary"]:hover {{
        background: {BLUE_HOVER} !important;
    }}
    [data-testid="stBaseButton-primary"]:active {{
        transform: scale(0.98);
    }}
    [data-testid="stBaseButton-primary"]:focus-visible {{
        box-shadow: 0 0 0 4px {BLUE_TINT} !important;
    }}

    /* ── Download buttons (secondary pill) ── */
    [data-testid="stDownloadButton"] > button {{
        background: {GROUPED} !important;
        border: none !important;
        border-radius: 980px !important;
        color: {BLUE} !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        padding: 0.6rem 1.1rem !important;
        transition: background 0.18s ease;
    }}
    [data-testid="stDownloadButton"] > button:hover {{
        background: #ebebef !important; color: {BLUE_HOVER} !important;
    }}

    /* ── Tabs styled as a segmented control ── */
    [data-testid="stTabs"] [role="tablist"] {{
        background: {GROUPED} !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 3px !important;
        gap: 2px !important;
        display: inline-flex !important;
        width: fit-content !important;
        align-self: flex-start !important;
    }}
    [data-testid="stTabs"] .react-aria-SelectionIndicator {{ display: none !important; }}
    [data-testid="stTab"] {{
        background: transparent !important;
        color: {INK} !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.35rem 1.05rem !important;
        transition: background 0.18s ease;
    }}
    [data-testid="stTab"] p {{
        font-size: 0.85rem !important; font-weight: 500 !important;
        font-family: {FONT} !important; margin: 0 !important;
    }}
    [data-testid="stTab"][data-selected="true"] {{
        background: {SURFACE} !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.10), 0 0 1px rgba(0,0,0,0.12) !important;
    }}
    [data-testid="stTabPanel"] {{ padding-top: 0.9rem !important; }}

    /* ── Expander ── */
    [data-testid="stExpander"] details {{
        background: {SURFACE} !important;
        border: 1px solid {HAIRLINE_L} !important;
        border-radius: 14px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    [data-testid="stExpander"] summary {{
        color: {INK} !important; font-weight: 500 !important; font-size: 0.9rem !important;
    }}
    [data-testid="stExpander"] summary:hover {{ color: {BLUE} !important; }}
    [data-testid="stExpander"] svg {{ fill: {INK_3} !important; }}

    /* ── Dataframe ── */
    [data-testid="stDataFrame"] {{
        border-radius: 14px !important;
        overflow: hidden !important;
        border: 1px solid {HAIRLINE_L} !important;
    }}

    /* ── Misc ── */
    [data-testid="stSpinner"] p {{ color: {INK_2} !important; font-size: 0.88rem; }}
    [data-testid="stAlert"] {{ border-radius: 14px !important; }}
    [data-testid="stElementContainer"]:has(.ad-rule) {{ margin: 0; }}
    </style>
    """, unsafe_allow_html=True)


# ── HTML helpers ─────────────────────────────────────────────────────────────

MARK_SVG = (
    '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="1.9" stroke-linecap="round" '
    'stroke-linejoin="round"><path d="M16 20v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>'
    '<circle cx="9" cy="7" r="3.2"/><path d="M22 20v-2a4 4 0 0 0-3-3.87"/>'
    '<path d="M16.5 3.6a4 4 0 0 1 0 6.8"/></svg>'
)

EMPTY_SVG = (
    f'<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="{HAIRLINE}" '
    'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">'
    '<rect x="3" y="3" width="18" height="18" rx="4"/><path d="M3 9h18"/>'
    '<path d="M9 9v12"/></svg>'
)


def rule() -> str:
    return '<div class="ad-rule"></div>'


def section_label(text: str) -> str:
    return f'<div class="ad-section">{text}</div>'


def field_row(label: str, value: str) -> str:
    return (f'<div class="ad-row"><span class="ad-label">{label}</span>'
            f'<span class="ad-value">{value}</span></div>')


def stat_card(label: str, value: str, color: str = INK) -> str:
    return (f'<div class="ad-stat"><div class="ad-stat-value" style="color:{color}">{value}</div>'
            f'<div class="ad-stat-label">{label}</div></div>')


def pill(key: str, value: str) -> str:
    key_html = f'<span class="k">{key}</span>' if key else ""
    return f'<span class="ad-pill">{key_html}<span class="v">{value}</span></span>'


def fmt_salary(value: int) -> str:
    return f"{value / 1_000_000:.1f}M"


def months_label(n: int, t: dict) -> str:
    unit = t["month_unit"] if n == 1 else t["months_unit"]
    return f"{n} {unit}".strip()


# ── Plotly theme ──────────────────────────────────────────────────────────────

_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=INK_2, family=PLOT_FONT, size=11),
    margin=dict(t=46, b=34, l=8, r=8),
    height=CHART_H,
    colorway=CHART_COLORS,
    legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0,
                font=dict(color=INK_2, size=11)),
    hoverlabel=dict(bgcolor=SURFACE, bordercolor=HAIRLINE,
                    font=dict(color=INK, family=PLOT_FONT, size=12)),
)
_AXIS = dict(showgrid=True, gridcolor="#ececee", zeroline=False,
             tickfont=dict(color=INK_3, size=10), linecolor=HAIRLINE)


def _chart_title(text: str) -> dict:
    return dict(text=text, x=0.5, xanchor="center",
                font=dict(color=INK, size=13, family=PLOT_FONT))


# ── Charts ────────────────────────────────────────────────────────────────────

def render_charts(df: pd.DataFrame, t: dict) -> None:
    first_month = df["base_date"].min()
    cdf = df[df["base_date"] == first_month].copy()
    if "is_primary_position" in cdf.columns:
        cdf = cdf[cdf["is_primary_position"] == True]

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1, st.container(border=True, key="adchart_gender"):
        gc = cdf.groupby("gender")["emp_id"].nunique().reset_index()
        gc.columns = ["Gender", "Count"]
        fig = go.Figure(go.Pie(
            labels=gc["Gender"], values=gc["Count"], hole=0.62, sort=False,
            marker=dict(colors=CHART_COLORS, line=dict(color=SURFACE, width=2)),
            textinfo="percent", insidetextorientation="horizontal",
            textfont=dict(color="#ffffff", size=11, family=PLOT_FONT),
        ))
        fig.update_layout(title=_chart_title(t["chart_gender_pie"]), **_LAYOUT)
        fig.update_layout(legend=dict(orientation="h", yanchor="top", y=-0.02,
                                      xanchor="center", x=0.5))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with c2, st.container(border=True, key="adchart_org"):
        oc = cdf.groupby("org_lv2")["emp_id"].nunique().reset_index()
        oc.columns = ["Dept", "Count"]
        oc = oc.sort_values("Count")
        fig = go.Figure(go.Bar(
            x=oc["Count"], y=oc["Dept"], orientation="h",
            marker=dict(color=BLUE, line=dict(width=0)),
            text=oc["Count"], textposition="outside", cliponaxis=False,
            textfont=dict(color=INK_3, size=10, family=PLOT_FONT),
        ))
        fig.update_layout(
            title=_chart_title(t["chart_org_bar"]),
            xaxis=dict(**_AXIS, title=""),
            yaxis=dict(showgrid=False, tickfont=dict(color=INK_2, size=10),
                       linecolor=HAIRLINE),
            bargap=0.45,
            **_LAYOUT,
        )
        fig.update_layout(margin=dict(t=46, b=34, l=8, r=36))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with c3, st.container(border=True, key="adchart_salary"):
        sdf = cdf[cdf["salary"].notna()].copy()
        if not sdf.empty:
            fig = px.box(sdf, x="position", y="salary", points="outliers",
                         color_discrete_sequence=[BLUE])
            fig.update_traces(
                quartilemethod="linear",
                marker=dict(size=3, opacity=0.45, color=BLUE),
                line=dict(color=BLUE, width=1.4),
                fillcolor="rgba(0,113,227,0.10)",
            )
            fig.update_layout(
                title=_chart_title(t["chart_salary_box"]),
                xaxis={**_AXIS, "title": "", "tickangle": -45,
                       "tickfont": dict(color=INK_3, size=9)},
                yaxis=dict(**_AXIS, title=""),
                **_LAYOUT,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── Config panel ──────────────────────────────────────────────────────────────

def render_config_panel(t: dict):
    """Render the left configuration panel. Returns the chosen values."""

    # ── Dataset ──
    st.markdown(section_label(t["dataset_section"]), unsafe_allow_html=True)
    with st.container(border=True, key="adgroup_dataset"):
        employee_count = st.session_state.get("employees", DEFAULT_EMPLOYEES)
        st.markdown(field_row(t["num_employees"], f"{employee_count:,}"),
                    unsafe_allow_html=True)
        employee_count = st.slider(
            t["num_employees"], MIN_EMPLOYEES, MAX_EMPLOYEES, DEFAULT_EMPLOYEES,
            label_visibility="collapsed", key="employees",
        )

        num_months = st.session_state.get("months", 1)
        st.markdown(field_row(t["num_months"], months_label(num_months, t)),
                    unsafe_allow_html=True)
        num_months = st.slider(t["num_months"], 1, 24, 1,
                               label_visibility="collapsed", key="months")

    # ── Ranges ──
    st.markdown(section_label(t["range_section"]), unsafe_allow_html=True)
    with st.container(border=True, key="adgroup_ranges"):
        age_range = st.session_state.get("age", (25, 55))
        st.markdown(
            field_row(t["age_range"], f'{age_range[0]}–{age_range[1]} {t["years_unit"]}'),
            unsafe_allow_html=True,
        )
        age_range = st.slider(t["age_range"], 18, 65, (25, 55),
                              label_visibility="collapsed", key="age")

        salary_range = st.session_state.get("salary", (4_000_000, 10_000_000))
        st.markdown(
            field_row(t["salary_range"],
                      f"{fmt_salary(salary_range[0])} – {fmt_salary(salary_range[1])}"),
            unsafe_allow_html=True,
        )
        salary_range = st.slider(
            t["salary_range"], 3_000_000, 30_000_000, (4_000_000, 10_000_000),
            step=500_000, label_visibility="collapsed", key="salary",
        )

    # ── Options ──
    st.markdown(section_label(t["options_section"]), unsafe_allow_html=True)
    toggle = getattr(st, "toggle", st.checkbox)
    with st.container(border=True, key="adgroup_options"):
        include_concurrent = toggle(
            t["include_concurrent"], value=False, help=t["concurrent_tooltip"],
        )

    st.markdown('<div style="height:1.4rem"></div>', unsafe_allow_html=True)
    generate = st.button(t["generate_button"], type="primary", use_container_width=True)

    st.markdown(
        '<div class="ad-foot">'
        '<a href="mailto:hrdata.generator@gmail.com">hrdata.generator@gmail.com</a><br>'
        '<a href="https://x.com/hrdata_gen">𝕏 @hrdata_gen</a></div>',
        unsafe_allow_html=True,
    )

    return employee_count, num_months, age_range, salary_range, include_concurrent, generate


# ── Result view ───────────────────────────────────────────────────────────────

def render_results(df: pd.DataFrame, t: dict) -> None:
    primary_df = df[df["is_primary_position"] == True] if "is_primary_position" in df.columns else df
    first_count = len(primary_df[primary_df["base_date"] == primary_df["base_date"].min()])
    resigned = df[df["resign_date"] != "2999-12-31"]["emp_id"].nunique()
    months_n = primary_df["base_date"].nunique()

    kpis = "".join([
        stat_card(t["kpi_rows"], f"{len(df):,}"),
        stat_card(t["kpi_headcount"], f"{first_count:,}"),
        stat_card(t["kpi_months"], str(months_n)),
        stat_card(t["kpi_resignations"], str(resigned)),
    ])
    st.markdown(
        f'<div style="display:flex;gap:12px;flex-wrap:wrap;margin:0.2rem 0 1.8rem">{kpis}</div>',
        unsafe_allow_html=True,
    )

    tab_charts, tab_preview, tab_dl = st.tabs([
        t["charts_title"], t["data_preview"], t["download_options"],
    ])

    with tab_charts:
        st.markdown(f'<p class="ad-note">{t["charts_note"]}</p>', unsafe_allow_html=True)
        render_charts(df, t)

    with tab_preview:
        shown = min(50, len(df))
        st.markdown(
            f'<p class="ad-note">'
            f'{t["preview_note"].format(shown=shown, total=len(df), cols=len(df.columns))}</p>',
            unsafe_allow_html=True,
        )
        st.dataframe(df.head(shown), use_container_width=True, height=440)

    with tab_dl:
        st.markdown(
            f'<p class="ad-note">'
            f'{t["download_note"].format(rows=len(df), cols=len(df.columns))}</p>',
            unsafe_allow_html=True,
        )
        d1, d2, d3, _ = st.columns([2, 2, 2, 4])

        d1.download_button(t["download_csv"], df.to_csv(index=False), "hr_data.csv",
                           "text/csv", use_container_width=True)

        buf = BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            df.to_excel(w, index=False)
        d2.download_button(t["download_excel"], buf.getvalue(), "hr_data.xlsx",
                           use_container_width=True)

        d3.download_button(t["download_json"], df.to_json(orient="records"),
                           "hr_data.json", "application/json", use_container_width=True)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    setup_page()
    inject_css()

    # ── Nav ───────────────────────────────────────────────────────────────
    nav_left, nav_right = st.columns([8, 2], vertical_alignment="center")
    with nav_left:
        st.markdown(
            f'<div class="ad-nav"><div class="ad-mark">{MARK_SVG}</div>'
            f'<div class="ad-wordmark">HR Data Generator</div></div>',
            unsafe_allow_html=True,
        )
    with nav_right:
        selected_language = st.selectbox(
            "Language / 言語", list(LANGUAGE_DATA.keys()), label_visibility="collapsed",
        )

    t = TRANSLATIONS[selected_language]
    st.markdown(rule(), unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="ad-hero"><h1>{t["title"]}</h1><p>{t["tagline"]}</p></div>',
        unsafe_allow_html=True,
    )

    # ── Config | content ──────────────────────────────────────────────────
    col_cfg, col_main = st.columns([4, 8], gap="large")

    with col_cfg:
        with st.container(border=False):
            (employee_count, num_months, age_range,
             salary_range, include_concurrent, generate) = render_config_panel(t)

    with col_main:
        st.markdown(
            f'<div class="ad-card" style="margin-bottom:1.15rem">'
            f'<div style="font-size:0.92rem;color:{INK_2};line-height:1.65">'
            f'{t["description"].replace(chr(10), "<br>")}</div></div>',
            unsafe_allow_html=True,
        )

        with st.expander(t["field_descriptions"], expanded=False):
            rows = "".join(
                f'<tr><td>{f}</td><td>{d}</td></tr>' for f, d in t["fields"].items()
            )
            st.markdown(
                f'<table class="ad-table"><thead><tr>'
                f'<th>{t["col_field"]}</th><th>{t["col_description"]}</th>'
                f'</tr></thead><tbody>{rows}</tbody></table>',
                unsafe_allow_html=True,
            )

        pills = "".join([
            pill(t["num_employees"], f"{employee_count:,}"),
            pill(t["num_months"], str(num_months)),
            pill(t["age_range"], f"{age_range[0]}–{age_range[1]}"),
            pill(t["salary_range"],
                 f"{fmt_salary(salary_range[0])}–{fmt_salary(salary_range[1])}"),
            pill("", selected_language),
        ])
        st.markdown(
            f'<div style="margin:1.15rem 0 1.5rem">{pills}</div>',
            unsafe_allow_html=True,
        )

        if not generate:
            st.markdown(
                f'<div class="ad-empty">{EMPTY_SVG}'
                f'<h3>{t["empty_title"]}</h3><p>{t["empty_body"]}</p></div>',
                unsafe_allow_html=True,
            )
            return

        with st.spinner(t["generating"]):
            try:
                config = GeneratorConfig(
                    language=selected_language,
                    employee_count=employee_count,
                    num_months=num_months,
                    age_range=age_range,
                    salary_range=salary_range,
                    include_concurrent_positions=include_concurrent,
                )
                df = generate_dataset(config)
            except Exception as e:
                st.error(f'{t["failed"]}: {e}')
                return

        if df.empty:
            st.warning(t["no_data"])
            return

        render_results(df, t)


if __name__ == "__main__":
    main()

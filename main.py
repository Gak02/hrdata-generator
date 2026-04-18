import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

from hr_generator.config import TRANSLATIONS, LANGUAGE_DATA, MIN_EMPLOYEES, MAX_EMPLOYEES, DEFAULT_EMPLOYEES
from hr_generator.models import GeneratorConfig
from hr_generator.generator import generate_dataset


# ── Design tokens ────────────────────────────────────────────────────────────
ACCENT   = "#6366f1"
ACCENT2  = "#818cf8"
BG_CARD  = "#1e1f2e"
BG_PANEL = "#181927"
BG_PAGE  = "#13141f"
TEXT     = "#e2e8f0"
TEXT_DIM = "#94a3b8"
BORDER   = "#2d2f45"
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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ── Base ── */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {BG_PAGE} !important;
        color: {TEXT};
        font-family: 'Inter', system-ui, sans-serif;
    }}
    [data-testid="stAppViewContainer"] > .main > .block-container {{
        padding: 1.6rem 2.4rem 4rem;
        max-width: 1400px;
    }}

    /* ── Hide Streamlit chrome + remove sidebar space ── */
    #MainMenu, footer, [data-testid="stToolbar"],
    [data-testid="stSidebar"], [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"] {{ display: none !important; }}
    /* Remove the left margin Streamlit adds when a sidebar exists */
    section[data-testid="stMain"] {{
        margin-left: 0 !important;
        padding-left: 0 !important;
    }}

    /* ── Typography ── */
    h1, h2, h3, h4, h5 {{
        color: {TEXT} !important;
        font-family: 'Inter', system-ui, sans-serif !important;
        letter-spacing: -0.02em;
    }}
    p, li, div {{ font-family: 'Inter', system-ui, sans-serif; }}

    /* ── Inputs ── */
    [data-baseweb="select"] > div {{
        background-color: #252639 !important;
        border: 1px solid {BORDER} !important;
        border-radius: 8px !important;
        color: {TEXT} !important;
        font-size: 0.85rem !important;
    }}
    [data-baseweb="select"] * {{ color: {TEXT} !important; }}
    [data-baseweb="menu"] {{ background-color: #252639 !important; }}
    [data-baseweb="option"]:hover {{ background-color: rgba(99,102,241,0.15) !important; }}

    /* ── Slider ── */
    [data-testid="stSlider"] .stSlider > div > div > div {{
        background: linear-gradient(90deg, {ACCENT}, {ACCENT2}) !important;
    }}
    [data-testid="stSlider"] div[data-baseweb="slider"] div:nth-child(3) {{
        background: {BORDER} !important;
    }}

    /* ── Checkbox ── */
    [data-testid="stCheckbox"] label {{ color: {TEXT} !important; font-size: 0.85rem !important; }}
    [data-testid="stCheckbox"] div[role="checkbox"] {{
        border-color: {BORDER} !important;
        background-color: transparent !important;
    }}
    [data-testid="stCheckbox"] div[role="checkbox"][aria-checked="true"] {{
        background-color: {ACCENT} !important;
        border-color: {ACCENT} !important;
    }}

    /* ── Primary button ── */
    button[kind="primary"] {{
        background: linear-gradient(135deg, {ACCENT} 0%, {ACCENT2} 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        color: #fff !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.65rem 1.6rem !important;
        letter-spacing: 0.01em;
        box-shadow: 0 4px 18px rgba(99,102,241,0.4) !important;
        transition: all 0.2s ease !important;
    }}
    button[kind="primary"]:hover {{
        transform: translateY(-1px);
        box-shadow: 0 6px 24px rgba(99,102,241,0.55) !important;
    }}

    /* ── Download buttons ── */
    [data-testid="stDownloadButton"] > button {{
        background: transparent !important;
        border: 1px solid {BORDER} !important;
        border-radius: 8px !important;
        color: {TEXT_DIM} !important;
        font-size: 0.83rem !important;
        padding: 0.5rem 0.9rem !important;
        transition: all 0.18s ease !important;
    }}
    [data-testid="stDownloadButton"] > button:hover {{
        border-color: {ACCENT} !important;
        color: {ACCENT2} !important;
        background: rgba(99,102,241,0.1) !important;
    }}

    /* ── Dataframe ── */
    [data-testid="stDataFrame"] {{
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid {BORDER} !important;
    }}

    /* ── Tabs ── */
    [data-baseweb="tab-list"] {{
        background: transparent !important;
        border-bottom: 1px solid {BORDER} !important;
        gap: 4px;
    }}
    [data-baseweb="tab"] {{
        background: transparent !important;
        color: {TEXT_DIM} !important;
        border: none !important;
        border-radius: 6px 6px 0 0 !important;
        font-size: 0.84rem !important;
        padding: 0.5rem 1.1rem !important;
        font-family: 'Inter', system-ui, sans-serif !important;
    }}
    [aria-selected="true"][data-baseweb="tab"] {{
        background: rgba(99,102,241,0.1) !important;
        color: {ACCENT2} !important;
        border-bottom: 2px solid {ACCENT} !important;
    }}

    /* ── Expander ── */
    [data-testid="stExpander"] details {{
        background: {BG_CARD} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 12px !important;
    }}
    [data-testid="stExpander"] summary {{
        color: {TEXT} !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
    }}
    [data-testid="stExpander"] summary:hover {{
        color: {ACCENT2} !important;
    }}

    /* ── Spinner ── */
    [data-testid="stSpinner"] p {{ color: {TEXT_DIM} !important; }}

    /* ── Alert ── */
    [data-testid="stAlert"] {{ border-radius: 10px !important; }}

    /* ── Slider label ── */
    [data-testid="stSlider"] label {{ color: {TEXT_DIM} !important; font-size: 0.8rem !important; }}

    /* ── Config panel column card (second horizontal block only, not the header row) ── */
    [data-testid="stHorizontalBlock"] ~ [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child {{
        background: {BG_PANEL} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 16px !important;
        padding: 1.4rem 1.3rem !important;
    }}

    /* ── Slider range min/max numbers ── */
    [data-testid="stSlider"] [data-testid="stTickBarMin"],
    [data-testid="stSlider"] [data-testid="stTickBarMax"] {{
        color: {TEXT_DIM} !important;
        font-size: 0.72rem !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ── HTML helpers ─────────────────────────────────────────────────────────────

def card(html: str, padding: str = "1.4rem 1.6rem") -> str:
    return (
        f'<div style="background:{BG_CARD};border:1px solid {BORDER};'
        f'border-radius:14px;padding:{padding};margin-bottom:1rem">'
        f'{html}</div>'
    )


def section_label(text: str) -> str:
    return (
        f'<div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;'
        f'color:{TEXT_DIM};margin:1.2rem 0 0.35rem;font-weight:600">{text}</div>'
    )


def stat_block(label: str, value: str, color: str = ACCENT2, sub: str = "") -> str:
    sub_html = f'<div style="font-size:0.7rem;color:{TEXT_DIM};margin-top:3px">{sub}</div>' if sub else ""
    return (
        f'<div style="background:{BG_CARD};border:1px solid {BORDER};border-radius:14px;'
        f'padding:1.1rem 1.3rem;flex:1;min-width:130px">'
        f'<div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.08em;'
        f'color:{TEXT_DIM};margin-bottom:6px">{label}</div>'
        f'<div style="font-size:1.7rem;font-weight:700;color:{color};line-height:1">{value}</div>'
        f'{sub_html}</div>'
    )


# ── Plotly dark theme ─────────────────────────────────────────────────────────

_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT_DIM, family="Inter, system-ui, sans-serif", size=11),
    margin=dict(t=40, b=32, l=8, r=8),
    colorway=[ACCENT, "#818cf8", "#a5b4fc", "#c7d2fe", "#34d399", "#fbbf24"],
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=BORDER, borderwidth=1),
)
_AXIS = dict(showgrid=True, gridcolor=BORDER, zeroline=False,
             tickfont=dict(color=TEXT_DIM, size=10), linecolor=BORDER)


def _chart_wrap(title: str) -> str:
    return (
        f'<div style="background:{BG_CARD};border:1px solid {BORDER};'
        f'border-radius:14px;padding:1rem 0.5rem 0.5rem;margin-bottom:0.5rem">'
        f'<div style="font-size:0.82rem;font-weight:600;color:{TEXT};'
        f'text-align:center;margin-bottom:0.3rem">{title}</div>'
    )


# ── Charts ────────────────────────────────────────────────────────────────────

def render_charts(df: pd.DataFrame, t: dict) -> None:
    first_month = df["base_date"].min()
    cdf = df[df["base_date"] == first_month].copy()
    if "is_primary_position" in cdf.columns:
        cdf = cdf[cdf["is_primary_position"] == True]

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        gc = cdf.groupby("gender")["emp_id"].nunique().reset_index()
        gc.columns = ["Gender", "Count"]
        fig = go.Figure(go.Pie(
            labels=gc["Gender"], values=gc["Count"], hole=0.55,
            marker=dict(colors=[ACCENT, "#818cf8", "#a5b4fc"],
                        line=dict(color=BG_PAGE, width=2)),
            textfont=dict(color=TEXT, size=11),
        ))
        fig.update_layout(
            title=dict(text=t["chart_gender_pie"], x=0.5,
                       font=dict(color=TEXT, size=12, family="Inter")),
            **_LAYOUT,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with c2:
        oc = cdf.groupby("org_lv2")["emp_id"].nunique().reset_index()
        oc.columns = ["Dept", "Count"]
        oc = oc.sort_values("Count")
        fig = go.Figure(go.Bar(
            x=oc["Count"], y=oc["Dept"], orientation="h",
            marker=dict(color=oc["Count"],
                        colorscale=[[0, "#3730a3"], [1, ACCENT2]], line=dict(width=0)),
            text=oc["Count"], textposition="outside",
            textfont=dict(color=TEXT_DIM, size=10),
        ))
        fig.update_layout(
            title=dict(text=t["chart_org_bar"], x=0.5,
                       font=dict(color=TEXT, size=12, family="Inter")),
            xaxis=dict(**_AXIS, title=""),
            yaxis=dict(showgrid=False, tickfont=dict(color=TEXT_DIM, size=10),
                       linecolor=BORDER),
            **_LAYOUT,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with c3:
        sdf = cdf[cdf["salary"].notna()].copy()
        if not sdf.empty:
            fig = px.box(sdf, x="position", y="salary", points="all",
                         color_discrete_sequence=[ACCENT])
            fig.update_traces(
                quartilemethod="linear", boxpoints="all", jitter=0.3, pointpos=0,
                marker=dict(size=3, opacity=0.4, color=ACCENT2),
                line=dict(color=ACCENT),
                fillcolor="rgba(99,102,241,0.15)",
            )
            fig.update_layout(
                title=dict(text=t["chart_salary_box"], x=0.5,
                           font=dict(color=TEXT, size=12, family="Inter")),
                xaxis=dict(**_AXIS, title="", tickangle=-30),
                yaxis=dict(**_AXIS, title=""),
                **_LAYOUT,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── Config panel ──────────────────────────────────────────────────────────────

def render_config_panel(t: dict, selected_language: str):
    """Render left-side configuration panel. Returns config values."""

    # Panel header
    st.markdown(
        f'<div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;'
        f'color:{TEXT_DIM};font-weight:600;margin-bottom:1rem">Configuration</div>',
        unsafe_allow_html=True,
    )

    # ── Core params ──
    st.markdown(section_label("Employees"), unsafe_allow_html=True)
    employee_count = st.slider(
        t["num_employees"], MIN_EMPLOYEES, MAX_EMPLOYEES, DEFAULT_EMPLOYEES,
        label_visibility="collapsed",
    )
    st.markdown(
        f'<div style="text-align:right;font-size:0.72rem;color:{ACCENT2};'
        f'margin-top:-10px;margin-bottom:8px;font-weight:600">{employee_count:,}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(section_label("Months"), unsafe_allow_html=True)
    num_months = st.slider(t["num_months"], 1, 24, 1, label_visibility="collapsed")
    st.markdown(
        f'<div style="text-align:right;font-size:0.72rem;color:{ACCENT2};'
        f'margin-top:-10px;margin-bottom:8px;font-weight:600">'
        f'{num_months} mo</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<hr style="border-color:{BORDER};margin:0.8rem 0">',
        unsafe_allow_html=True,
    )

    # ── Additional params ──
    st.markdown(
        f'<div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;'
        f'color:{TEXT_DIM};font-weight:600;margin-bottom:0.6rem">Parameters</div>',
        unsafe_allow_html=True,
    )

    st.markdown(section_label("Age range"), unsafe_allow_html=True)
    age_range = st.slider(t["age_range"], 18, 65, (25, 55), label_visibility="collapsed")
    st.markdown(
        f'<div style="text-align:right;font-size:0.72rem;color:{ACCENT2};'
        f'margin-top:-10px;margin-bottom:8px;font-weight:600">'
        f'{age_range[0]}–{age_range[1]} yrs</div>',
        unsafe_allow_html=True,
    )

    st.markdown(section_label("Salary range"), unsafe_allow_html=True)
    salary_range = st.slider(
        t["salary_range"], 3_000_000, 30_000_000, (4_000_000, 10_000_000),
        step=500_000, label_visibility="collapsed",
    )
    st.markdown(
        f'<div style="text-align:right;font-size:0.72rem;color:{ACCENT2};'
        f'margin-top:-10px;margin-bottom:8px;font-weight:600">'
        f'{salary_range[0]//1_000_000:.1f}M – {salary_range[1]//1_000_000:.1f}M</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<hr style="border-color:{BORDER};margin:0.8rem 0">',
        unsafe_allow_html=True,
    )

    include_concurrent = st.checkbox(
        t["include_concurrent"],
        value=False,
        help=t["concurrent_tooltip"],
    )

    st.markdown(
        f'<hr style="border-color:{BORDER};margin:1rem 0">',
        unsafe_allow_html=True,
    )

    # Generate button
    generate = st.button(
        t["generate_button"], type="primary", use_container_width=True
    )

    # Footer
    st.markdown(
        f'<div style="font-size:0.7rem;color:{TEXT_DIM};line-height:2;margin-top:1.6rem">'
        f'📧 hrdata.generator@gmail.com<br>𝕏 @hrdata_gen</div>',
        unsafe_allow_html=True,
    )

    return employee_count, num_months, age_range, salary_range, include_concurrent, generate


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    setup_page()
    inject_css()

    # ── Global header ─────────────────────────────────────────────────────
    h_left, h_right = st.columns([7, 2])
    with h_left:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:14px;padding:0 0 1.2rem">'
            f'<div style="width:44px;height:44px;flex-shrink:0;border-radius:13px;'
            f'background:linear-gradient(135deg,{ACCENT},{ACCENT2});'
            f'display:flex;align-items:center;justify-content:center;font-size:1.3rem">👥</div>'
            f'<div>'
            f'<div style="font-size:1.4rem;font-weight:700;color:{TEXT};'
            f'line-height:1.1;letter-spacing:-0.02em">HR Data Generator</div>'
            f'<div style="font-size:0.68rem;color:{TEXT_DIM};margin-top:3px;'
            f'text-transform:uppercase;letter-spacing:0.08em">'
            f'Synthetic workforce dataset builder</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    with h_right:
        selected_language = st.selectbox(
            "Language / 言語", list(LANGUAGE_DATA.keys()),
            label_visibility="collapsed",
        )

    t = TRANSLATIONS[selected_language]

    st.markdown(
        f'<hr style="border-color:{BORDER};margin:0 0 1.4rem">',
        unsafe_allow_html=True,
    )

    # ── Two-column layout: config | content ───────────────────────────────
    col_cfg, col_main = st.columns([3, 9], gap="large")

    # ── Config panel ──────────────────────────────────────────────────────
    with col_cfg:
        (employee_count, num_months, age_range,
         salary_range, include_concurrent, generate) = render_config_panel(t, selected_language)

    # ── Main content ──────────────────────────────────────────────────────
    with col_main:

        # Description
        st.markdown(
            card(
                f'<div style="font-size:0.86rem;color:{TEXT_DIM};line-height:1.75">'
                f'{t["description"].replace(chr(10), "<br>")}</div>'
            ),
            unsafe_allow_html=True,
        )

        # Field reference (collapsible)
        with st.expander(f"📋  {t['field_descriptions']}", expanded=False):
            rows = "".join(
                f'<tr style="border-bottom:1px solid {BORDER}">'
                f'<td style="padding:7px 14px;font-weight:500;color:{ACCENT2};'
                f'white-space:nowrap;font-size:0.8rem">{f}</td>'
                f'<td style="padding:7px 14px;color:{TEXT_DIM};font-size:0.8rem">{d}</td>'
                f'</tr>'
                for f, d in t["fields"].items()
            )
            st.markdown(
                f'<table style="width:100%;border-collapse:collapse">'
                f'<thead><tr style="border-bottom:2px solid {BORDER}">'
                f'<th style="padding:7px 14px;text-align:left;color:{TEXT};font-size:0.73rem;'
                f'text-transform:uppercase;letter-spacing:0.08em">Field</th>'
                f'<th style="padding:7px 14px;text-align:left;color:{TEXT};font-size:0.73rem;'
                f'text-transform:uppercase;letter-spacing:0.08em">Description</th>'
                f'</tr></thead><tbody>{rows}</tbody></table>',
                unsafe_allow_html=True,
            )

        # Config pills
        def pill(k, v):
            return (
                f'<span style="display:inline-flex;align-items:center;gap:5px;'
                f'background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.25);'
                f'border-radius:20px;padding:3px 10px;font-size:0.75rem;margin:2px">'
                f'<span style="color:{TEXT_DIM}">{k}</span>'
                f'<span style="color:{ACCENT2};font-weight:600">{v}</span></span>'
            )

        pills = "".join([
            pill("employees", f"{employee_count:,}"),
            pill("months", str(num_months)),
            pill("age", f"{age_range[0]}–{age_range[1]}"),
            pill("salary", f"{salary_range[0]//1_000_000:.1f}M–{salary_range[1]//1_000_000:.1f}M"),
            pill("concurrent", "on" if include_concurrent else "off"),
            pill("lang", selected_language),
        ])
        st.markdown(
            f'<div style="display:flex;flex-wrap:wrap;gap:2px;margin:0.8rem 0 1.4rem">'
            f'{pills}</div>',
            unsafe_allow_html=True,
        )

        # ── Generation result ────────────────────────────────────────────
        if generate:
            spinner_msg = "Generating data…" if selected_language == "English" else "データを生成中…"
            with st.spinner(spinner_msg):
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
                    st.error(f"Generation failed: {e}")
                    return

            if df.empty:
                st.warning("No data generated — adjust parameters and try again.")
                return

            # KPI strip
            primary_df = df[df["is_primary_position"] == True] if "is_primary_position" in df.columns else df
            first_count = len(primary_df[primary_df["base_date"] == primary_df["base_date"].min()])
            resigned = df[df["resign_date"] != "2999-12-31"]["emp_id"].nunique()
            months_n = primary_df["base_date"].nunique()

            kpis = "".join([
                stat_block("Total rows", f"{len(df):,}"),
                stat_block("Headcount (M1)", f"{first_count:,}"),
                stat_block("Months", str(months_n)),
                stat_block("Resignations", str(resigned), color="#f87171"),
            ])
            st.markdown(
                f'<div style="display:flex;gap:10px;flex-wrap:wrap;margin:0.2rem 0 1.4rem">'
                f'{kpis}</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                f'<hr style="border-color:{BORDER};margin:0 0 1rem">',
                unsafe_allow_html=True,
            )

            # Tabs
            tab_charts, tab_preview, tab_dl = st.tabs([
                "📊  " + t["charts_title"],
                "🔍  " + t["data_preview"],
                "💾  " + t["download_options"],
            ])

            with tab_charts:
                st.markdown(
                    f'<p style="font-size:0.75rem;color:{TEXT_DIM};margin:0.6rem 0 1rem">'
                    f'Snapshot based on first month · primary positions only</p>',
                    unsafe_allow_html=True,
                )
                render_charts(df, t)

            with tab_preview:
                st.markdown(
                    f'<p style="font-size:0.75rem;color:{TEXT_DIM};margin:0.6rem 0 0.8rem">'
                    f'Showing first 50 of {len(df):,} rows · {len(df.columns)} columns</p>',
                    unsafe_allow_html=True,
                )
                st.dataframe(df.head(50), use_container_width=True, height=440)

            with tab_dl:
                st.markdown(
                    f'<p style="font-size:0.82rem;color:{TEXT_DIM};margin:0.6rem 0 1.2rem">'
                    f'{len(df):,} rows · {len(df.columns)} columns</p>',
                    unsafe_allow_html=True,
                )
                d1, d2, d3, _ = st.columns([2, 2, 2, 4])

                csv = df.to_csv(index=False)
                d1.download_button("⬇  CSV", csv, "hr_data.csv", "text/csv",
                                   use_container_width=True)

                buf = BytesIO()
                with pd.ExcelWriter(buf, engine="openpyxl") as w:
                    df.to_excel(w, index=False)
                d2.download_button("⬇  Excel", buf.getvalue(), "hr_data.xlsx",
                                   use_container_width=True)

                d3.download_button("⬇  JSON", df.to_json(orient="records"),
                                   "hr_data.json", "application/json",
                                   use_container_width=True)


if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

from hr_generator.config import TRANSLATIONS, LANGUAGE_DATA, MIN_EMPLOYEES, MAX_EMPLOYEES, DEFAULT_EMPLOYEES
from hr_generator.models import GeneratorConfig
from hr_generator.generator import generate_dataset


def setup_page():
    st.set_page_config(
        page_title="HR Data Generator",
        page_icon="👥",
        layout="wide",
    )


def render_charts(df, t):
    """Render visualization charts for the generated data."""
    st.subheader(t["charts_title"])

    # Use only first month and primary positions for charts
    first_month = df["base_date"].min()
    chart_df = df[df["base_date"] == first_month].copy()
    if "is_primary_position" in chart_df.columns:
        chart_df = chart_df[chart_df["is_primary_position"] == True]

    # Display all 3 charts in parallel columns
    col1, col2, col3 = st.columns(3)

    # 1. Gender pie chart
    with col1:
        gender_counts = chart_df["gender"].value_counts().reset_index()
        gender_counts.columns = ["Gender", "Count"]
        fig_gender = px.pie(
            gender_counts,
            values="Count",
            names="Gender",
            title=t["chart_gender_pie"],
        )
        st.plotly_chart(fig_gender, use_container_width=True)

    # 2. Headcount by org_lv2 (bar chart)
    with col2:
        org_counts = chart_df["org_lv2"].value_counts().reset_index()
        org_counts.columns = ["Department", "Count"]
        fig_org = px.bar(
            org_counts,
            x="Department",
            y="Count",
            title=t["chart_org_bar"],
        )
        fig_org.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_org, use_container_width=True)

    # 3. Salary box plot by position (vertical box plots: position on x-axis, salary on y-axis)
    with col3:
        salary_df = chart_df[chart_df["salary"].notna()].copy()
        if not salary_df.empty:
            fig_salary = px.box(
                salary_df,
                x="position",
                y="salary",
                title=t["chart_salary_box"],
                labels={"position": "Position", "salary": "Salary"},
            )
            fig_salary.update_traces(
                quartilemethod="linear",
            )
            fig_salary.update_layout(
                xaxis_tickangle=-45,
                yaxis_title="Salary",
                xaxis_title="Position",
            )
            st.plotly_chart(fig_salary, use_container_width=True)


def main():
    setup_page()

    # Language selection
    selected_language = st.selectbox("Language / 言語", list(LANGUAGE_DATA.keys()))
    t = TRANSLATIONS[selected_language]

    # UI Setup
    st.title(t["title"])
    st.markdown(t["description"])

    # Field descriptions
    fields = list(t["fields"].keys())
    descriptions = [t["fields"][field] for field in fields]
    df_desc = pd.DataFrame({"Field": fields, "Description": descriptions})
    st.subheader(t["field_descriptions"])
    st.table(df_desc)

    # Sidebar configuration
    st.sidebar.header(t["config"])

    employee_count = st.sidebar.slider(t["num_employees"], MIN_EMPLOYEES, MAX_EMPLOYEES, DEFAULT_EMPLOYEES)
    num_months = st.sidebar.slider(t["num_months"], 1, 24, 1)

    st.sidebar.subheader(t["additional_params"])
    age_range = st.sidebar.slider(t["age_range"], 18, 65, (25, 55))
    salary_range = st.sidebar.slider(t["salary_range"], 3000000, 30000000, (4000000, 10000000))

    # Concurrent positions option
    include_concurrent = st.sidebar.checkbox(
        t["include_concurrent"],
        value=False,
        help=t["concurrent_tooltip"],
    )

    # Build config
    config = GeneratorConfig(
        language=selected_language,
        employee_count=employee_count,
        num_months=num_months,
        age_range=age_range,
        salary_range=salary_range,
        include_concurrent_positions=include_concurrent,
    )

    # Generate data
    if st.button(t["generate_button"], type="primary"):
        with st.spinner("Generating data..." if selected_language == "English" else "データを生成中..."):
            try:
                df = generate_dataset(config)
                if not df.empty:
                    # Data preview
                    st.subheader(t["data_preview"])
                    st.dataframe(df.head(10))

                    # Download options (before charts)
                    st.subheader(t["download_options"])
                    col1, col2, col3 = st.columns(3)

                    csv = df.to_csv(index=False)
                    col1.download_button(t["download_csv"], csv, "hr_data.csv", "text/csv")

                    excel_buffer = BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                        df.to_excel(writer, index=False)
                    col2.download_button(t["download_excel"], excel_buffer.getvalue(), "hr_data.xlsx")

                    json_data = df.to_json(orient="records")
                    col3.download_button(t["download_json"], json_data, "hr_data.json", "application/json")

                    # Charts (after download options)
                    render_charts(df, t)
            except Exception as e:
                st.error(f"Error generating data: {str(e)}")

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    ### {t["contact"]}
    - **email**: hrdata.generator@gmail.com
    - **X account**: @hrdata_gen
    """)


if __name__ == "__main__":
    main()

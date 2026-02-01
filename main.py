import streamlit as st
import pandas as pd
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

    # Build config
    config = GeneratorConfig(
        language=selected_language,
        employee_count=employee_count,
        num_months=num_months,
        age_range=age_range,
        salary_range=salary_range,
    )

    # Generate data
    if st.button(t["generate_button"], type="primary"):
        with st.spinner("Generating data..." if selected_language == "English" else "データを生成中..."):
            try:
                df = generate_dataset(config)
                if not df.empty:
                    st.subheader(t["data_preview"])
                    st.dataframe(df.head(10))

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

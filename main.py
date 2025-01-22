import streamlit as st
import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import numpy as np
from dateutil.relativedelta import relativedelta
from io import BytesIO

# Language-specific data
LANGUAGE_DATA = {
    "English": {
        "organizations": {
            "org_lv1": ["Hogehoge inc."],
            "org_lv2": ["Sales & Marketing", "Engineering", "HR", "Finance"],
            "org_lv3": {
                "Sales": ["Global Sales", "Regional Sales", "Sales Operations", "Business Development"],
                "Engineering": ["Software Development", "Cloud Infrastructure", "Data Engineering", "Product Development"],
                "HR": ["Talent Acquisition", "People Operations", "Learning & Development", "HR Operations"],
                "Finance": ["Financial Planning", "Accounting", "Treasury", "Internal Audit"]
            },
            "org_lv4": ["Team Alpha", "Team Beta", "Team Gamma", "Team Delta", "Team Epsilon"]
        },
        "positions": {
            "choices": ["Staff", "Team Lead", "Manager", "General Manager", "VP", "C-level"],
            "weights": [50, 30, 10, 5, 3, 2]
        },
        "emp_types": {
            "choices": ["Full-time", "Contract", "Temporary"],
            "weights": [70, 20, 10]
        },
        "job_categories": {
            "Sales": ["Sales Representative", "Account Manager", "Sales Operations", "Business Development"],
            "Engineering": ["Software Engineer", "Data Engineer", "Cloud Architect", "DevOps Engineer"],
            "HR": ["HR Specialist", "Recruiter", "HR Operations", "Training Specialist"],
            "Finance": ["Financial Analyst", "Accountant", "Treasury Analyst", "Auditor"]
        },
        "genders": ["Male", "Female", "Other"],
        "cities": {
            "major": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
            "other": ["Seattle", "Boston", "Denver", "Austin", "Portland"]
        }
    },
    "Japanese": {
        "organizations": {
            "org_lv1": ["株式会社hogehoge"],
            "org_lv2": ["営業・マーケティング", "エンジニアリング", "人事", "財務"],
            "org_lv3": {
                "Sales": ["グローバル営業", "国内営業", "営業管理", "事業開発"],
                "Engineering": ["ソフトウェア開発", "クラウドインフラ", "データエンジニアリング", "製品開発"],
                "HR": ["採用", "人事オペレーション", "人材開発", "労務管理"],
                "Finance": ["経営企画", "経理", "財務", "内部監査"]
            },
            "org_lv4": ["第一チーム", "第二チーム", "第三チーム", "第四チーム", "第五チーム"]
        },
        "positions": {
            "choices": ["一般社員", "チームリーダー", "マネージャー", "部長", "執行役員", "取締役"],
            "weights": [50, 30, 10, 5, 3, 2]
        },
        "emp_types": {
            "choices": ["正社員", "契約社員", "派遣社員"],
            "weights": [70, 20, 10]
        },
        "job_categories": {
            "Sales": ["営業担当", "アカウントマネージャー", "営業管理", "事業開発"],
            "Engineering": ["ソフトウェアエンジニア", "データエンジニア", "クラウドアーキテクト", "DevOpsエンジニア"],
            "HR": ["人事担当", "採用担当", "人事業務", "研修担当"],
            "Finance": ["財務アナリスト", "経理担当", "財務担当", "監査担当"]
        },
        "genders": ["男性", "女性", "その他"],
        "cities": {
            "major": ["東京", "横浜", "大阪", "名古屋", "福岡"],
            "other": ["札幌", "仙台", "広島", "神戸", "京都"]
        }
    }
}

# Language dictionaries for UI
TRANSLATIONS = {
    "English": {
        "title": "🪄 HR Data Generator",
        "description": "This app generates sample HR data for 1-24 months with realistic employee information.\nYou can customise various parameters and download the generated dataset in multiple formats.",
        "config": "⚙️ Configuration",
        "language": "Select Language",
        "num_employees": "Number of Employees",
        "num_months": "Number of Months",
        "additional_params": "Additional Parameters",
        "age_range": "Age Range",
        "salary_range": "Salary Range (JPY)",
        "include_side_jobs": "Include subaffiliated jobs",
        "side_jobs_help": "Generate additional subaffiliated job records for some employees",
        "generate_button": "Generate HR Data",
        "data_preview": "Data Preview",
        "download_options": "Download Options",
        "download_csv": "Download CSV",
        "download_excel": "Download Excel",
        "download_json": "Download JSON",
        "field_descriptions": "Field Descriptions",
        "contact": "Contact",
        "fields": {
            "Employee ID": "Unique identifier for each employee",
            "Name": "Full name of the employee",
            "Birth date": "Employee's birth date",
            "Gender": "Employee's gender identity",
            "Organisation": "Four-level organisational hierarchy",
            "Emp Type": "Type of employment (full-time, contract, outsourced)",
            "Position": "Job title/role",
            "Salary": "Annual salary in JPY",
            "Hire Date": "Employment start date",
            "Resign Date": "Employment end date (if applicable)",
            "Engagement Score": "Employee engagement score",
            "Performance": "Annual performance result",
            "Marital Status": "Whether the employee is married",
            "Address": "Employee's address",
            "Job Category": "Functional or professional category for the job",
            "Job Grade": "Grade of the job within the company",
            "Base date": "Date at when data is generated"
        }
    },
    "Japanese": {
        "title": "🪄 人事データ生成ツール",
        "description": "このアプリは、1~24ヶ月分の現実的な従業員情報を生成します。\nさまざまなパラメータをカスタマイズして、生成したデータセットを複数の形式でダウンロードできます。",
        "config": "⚙️ 設定",
        "language": "言語選択",
        "num_employees": "従業員数",
        "num_months": "生成月数",
        "additional_params": "追加パラメータ",
        "age_range": "年齢範囲",
        "salary_range": "給与範囲（円）",
        "include_side_jobs": "兼務を含める",
        "side_jobs_help": "一部の従業員の兼務レコードを生成します",
        "generate_button": "データを生成",
        "data_preview": "データプレビュー",
        "download_options": "ダウンロードオプション",
        "download_csv": "CSVダウンロード",
        "download_excel": "Excelダウンロード",
        "download_json": "JSONダウンロード",
        "field_descriptions": "フィールドの説明",
        "contact": "お問い合わせ",
        "fields": {
            "Employee ID": "従業員の一意の識別子",
            "Name": "従業員氏名",
            "Birth date": "生年月日",
            "Gender": "性別",
            "Organisation": "4階層の組織階層",
            "Emp Type": "雇用形態（正社員、契約社員、派遣社員）",
            "Position": "役職",
            "Salary": "年間給与（円）",
            "Hire Date": "入社日",
            "Resign Date": "退職日（該当する場合）",
            "Engagement Score": "従業員エンゲージメントスコア",
            "Performance": "評価",
            "Marital Status": "婚姻状況",
            "Address": "住所",
            "Job Category": "職種",
            "Job Grade": "職務グレード",
            "Base date": "基準日"
        }
    }
}

# Set page configuration
st.set_page_config(
    page_title="HR Data Generator",
    page_icon="👥",
    layout="wide"
)

# Language selection at the very top
languages = {
    "English": "en_US",
    "Japanese": "ja_JP"
}

selected_language = st.selectbox(
    "Language / 言語",
    list(languages.keys())
)

# Get translations and language-specific data
t = TRANSLATIONS[selected_language]
lang_data = LANGUAGE_DATA[selected_language]

# Application title and description
st.title(t["title"])
st.markdown(t["description"])

# Field names and descriptions for the selected language
fields = list(t["fields"].keys())
descriptions = [t["fields"][field] for field in fields]

# Create data frame and display field descriptions on the main body
data = {"Field": fields, "Description": descriptions}
df = pd.DataFrame(data)

st.subheader(t["field_descriptions"])
st.table(df)

# Sidebar for parameters
st.sidebar.header(t["config"])

# Initialize Faker with selected locale
fake = Faker(languages[selected_language])

# Employee count selection
employee_count = st.sidebar.slider(
    t["num_employees"],
    min_value=200,
    max_value=500,
    value=300,
    help=t["num_employees"]
)

# Sidebar for number of months
num_months = st.sidebar.slider(
    t["num_months"],
    min_value=1,
    max_value=24,
    value=1,
    help=t["num_months"]
)

# Additional parameters
st.sidebar.subheader(t["additional_params"])
age_range = st.sidebar.slider(
    t["age_range"],
    min_value=18,
    max_value=65,
    value=(25, 55)
)

salary_range = st.sidebar.slider(
    t["salary_range"],
    min_value=3000000,
    max_value=30000000,
    value=(4000000, 10000000)
)

include_side_jobs = st.sidebar.checkbox(
    t["include_side_jobs"],
    value=False,
    help=t["side_jobs_help"]
)

# Define position hierarchy and corresponding salary multiplier
position_hierarchy = {
    lang_data["positions"]["choices"][0]: 1,
    lang_data["positions"]["choices"][1]: 1.2,
    lang_data["positions"]["choices"][2]: 1.5,
    lang_data["positions"]["choices"][3]: 2,
    lang_data["positions"]["choices"][4]: 2.5,
    lang_data["positions"]["choices"][5]: 3
}

# job grade mapping
position_to_grade = {
    lang_data["positions"]["choices"][0]: "Lv1",
    lang_data["positions"]["choices"][1]: "Lv2",
    lang_data["positions"]["choices"][2]: "Lv3",
    lang_data["positions"]["choices"][3]: "Lv4",
    lang_data["positions"]["choices"][4]: "Lv5",
    lang_data["positions"]["choices"][5]: "Lv6"
}

def generate_employee_data():
    """Generate employee data based on selected parameters"""
    data = []
    current_date = datetime.now()
    base_employees = []

    # Generate base employee information (common across all months)
    for i in range(employee_count):
        employee = {}

        employee["emp_id"] = f"EMP{str(i+1).zfill(6)}"
        employee["name"] = fake.name()

        age = random.randint(age_range[0], age_range[1])
        birth_date = current_date - relativedelta(years=age)
        employee["birth_date"] = birth_date.strftime("%Y-%m-%d")

        employee["gender"] = random.choice(lang_data["genders"])

        employee["org_lv1"] = random.choice(lang_data["organizations"]["org_lv1"])
        employee["org_lv2"] = random.choice(lang_data["organizations"]["org_lv2"])
        # Map org_lv2 to department key
        dept_key = "Sales"  # Default
        if "Engineering" in employee["org_lv2"] or "エンジニアリング" in employee["org_lv2"]:
            dept_key = "Engineering"
        elif "HR" in employee["org_lv2"] or "人事" in employee["org_lv2"]:
            dept_key = "HR"
        elif "Finance" in employee["org_lv2"] or "財務" in employee["org_lv2"]:
            dept_key = "Finance"

        org_lv3_options = lang_data["organizations"]["org_lv3"][dept_key]
        employee["org_lv3"] = random.choice(org_lv3_options)
        employee["org_lv4"] = random.choice(lang_data["organizations"]["org_lv4"])

        employee["position"] = random.choices(
            lang_data["positions"]["choices"],
            weights=lang_data["positions"]["weights"],
            k=1
        )[0]

        employee["emp_type"] = random.choices(
            lang_data["emp_types"]["choices"],
            weights=lang_data["emp_types"]["weights"],
            k=1
        )[0]

        if employee["emp_type"] == lang_data["emp_types"]["choices"][2]:  # Temporary/Outsourced
            employee["salary"] = None
            employee["engagement_score"] = None
            employee["performance"] = None
            employee["address"] = None
            employee["job_grade"] = None
            employee["position"] = lang_data["positions"]["choices"][0]  # Staff level

        else:
            hierarchy_multiplier = position_hierarchy.get(employee["position"], 1)
            normalized_multiplier = (hierarchy_multiplier - 1) / (max(position_hierarchy.values()) - 1)
            base_salary = salary_range[0] + (salary_range[1] - salary_range[0]) * normalized_multiplier
            employee["salary"] = round(base_salary, -3)


            max_years_ago = 20
            days_ago = random.randint(0, 365 * max_years_ago)
            employee["hire_date"] = (current_date - timedelta(days=days_ago)).strftime("%Y-%m-%d")

            if random.random() < 0.05:
                resign_days_ago = random.randint(0, 365)
                employee["resign_date"] = (current_date - timedelta(days=resign_days_ago)).strftime("%Y-%m-%d")
            else:
                employee["resign_date"] = None

            employee["engagement_score"] = round(random.uniform(14, 100), 0)

            engagement_score = employee.get("engagement_score", random.uniform(0, 100))
            if engagement_score >= 90:
                employee["performance"] = "S"
            elif engagement_score >= 75:
                employee["performance"] = "A"
            elif engagement_score >= 50:
                employee["performance"] = "B"
            else:
                employee["performance"] = "C"

            employee["is_married"] = random.choice([True, False])

            employee["address"] = random.choice(
                lang_data["cities"]["major"] if random.random() < 0.8 else lang_data["cities"]["other"]
            )

            if employee["position"] in ["執行役員", "取締役", "VP", "C-level"]:
                employee["job_category"] = "Management"
            else:
                categories = lang_data["job_categories"][dept_key]
                employee["job_category"] = random.choice(categories)

            employee["job_grade"] = position_to_grade.get(employee["position"], "Lv1")

        base_employees.append(employee)

    # Generate data for each month
    for month_offset in range(num_months):
        base_date = (current_date - timedelta(days=30 * (num_months - 1 - month_offset))).replace(day=1).strftime("%Y-%m-%d")
        for base_employee in base_employees:
            employee = base_employee.copy()
            employee["base_date"] = base_date

            if employee["emp_type"] != lang_data["emp_types"]["choices"][2]:  # Skip temporary employees for updates
                if employee.get("engagement_score") and random.random() < 0.3:
                    employee["engagement_score"] = round(employee["engagement_score"] * random.uniform(0.9, 1.1), 0)
                    engagement_score = employee["engagement_score"]
                    if engagement_score >= 90:
                        employee["performance"] = "S"
                    elif engagement_score >= 75:
                        employee["performance"] = "A"
                    elif engagement_score >= 50:
                        employee["performance"] = "B"
                    else:
                        employee["performance"] = "C"

                if employee.get("performance") and random.random() < 0.2:
                    current_salary = employee["salary"]
                    if employee["performance"] == "S":
                        employee["salary"] = round(current_salary * 1.1, -3)
                    elif employee["performance"] == "A":
                        employee["salary"] = round(current_salary * 1.05, -3)
                    elif employee["performance"] == "B":
                        employee["salary"] = round(current_salary * 1.02, -3)
                    elif employee["performance"] == "C":
                        employee["salary"] = round(current_salary * 0.98, -3)

            data.append(employee)

    return pd.DataFrame(data)


# Generate button
if st.button(t["generate_button"], type="primary"):
    df = generate_employee_data()
    st.subheader(t["data_preview"])
    st.dataframe(df.head(10))

    st.subheader(t["download_options"])

    col1, col2, col3 = st.columns(3)

    csv = df.to_csv(index=False)
    col1.download_button(
        label=t["download_csv"],
        data=csv,
        file_name="hr_data.csv",
        mime="text/csv"
    )

    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    excel_data = excel_buffer.getvalue()
    col2.download_button(
        label=t["download_excel"],
        data=excel_data,
        file_name="hr_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    json = df.to_json(orient="records")
    col3.download_button(
        label=t["download_json"],
        data=json,
        file_name="hr_data.json",
        mime="application/json"
    )

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
### {t["contact"]}
- **email**: hrdata.generator@gmail.com
- **X account**: @hrdata_gen
""")

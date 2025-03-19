import streamlit as st
import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta
import numpy as np
from dateutil.relativedelta import relativedelta
from io import BytesIO

# Constants
PERFORMANCE_THRESHOLDS = {
    "S": 90,
    "A": 75,
    "B": 50,
    "C": 0
}

SALARY_ADJUSTMENT_RATES = {
    "S": 1.20,
    "A": 1.10,
    "B": 1.05,
    "C": 0.97
}

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
            "weights": [50, 30, 10, 5, 3, 2],
            "hierarchy": {
                "executive": ["VP", "C-level"],
                "director": ["General Manager"],
                "manager": ["Manager"]
            }
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
            "weights": [50, 30, 10, 5, 3, 2],
            "hierarchy": {
                "executive": ["執行役員", "取締役"],
                "director": ["部長"],
                "manager": ["マネージャー"]
            }
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
        "description": "This application generates sample HR data for multiple months with realistic employee information.\nYou can customise various parameters and download the generated dataset in multiple formats.",
        "config": "⚙️ Configuration",
        "language": "Select Language",
        "num_employees": "Number of Employees",
        "num_months": "Number of Months",
        "additional_params": "Additional Parameters",
        "age_range": "Age Range",
        "salary_range": "Salary Range (JPY)",
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
            "Salary": "Annual salary in JPY *Update every 12 months based on performance",
            "Hire Date": "Employment start date",
            "Resign Date": "Employment end date (if applicable)",
            "Engagement Score": "Employee engagement score",
            "Performance": "Annual performance result *Update every 12 months",
            "Marital Status": "Whether the employee is married",
            "Address": "Employee's address",
            "Job Category": "Functional or professional category for the job",
            "Job Grade": "Grade or level of the job within the company",
            "Base date": "Date at when data is generated"
        }
    },
    "Japanese": {
        "title": "🪄 人事データ生成ツール",
        "description": "このアプリケーションは、1~24ヶ月分の現実的な従業員情報を生成します。\nさまざまなパラメータをカスタマイズして、生成したデータセットを複数の形式でダウンロードできます。",
        "config": "⚙️ 設定",
        "language": "言語選択",
        "num_employees": "従業員数",
        "num_months": "生成月数",
        "additional_params": "追加パラメータ",
        "age_range": "年齢範囲",
        "salary_range": "給与範囲（円）",
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
            "Salary": "年間給与（円） *評価をもとに12ヶ月ごとに更新",
            "Hire Date": "入社日",
            "Resign Date": "退職日（該当する場合）",
            "Engagement Score": "従業員エンゲージメントスコア",
            "Performance": "評価 *12ヶ月ごとに更新",
            "Marital Status": "婚姻状況",
            "Address": "住所",
            "Job Category": "職種",
            "Job Grade": "職務グレード",
            "Base date": "基準日"
        }
    }
}

def setup_page():
    st.set_page_config(
        page_title="HR Data Generator",
        page_icon="👥",
        layout="wide"
    )

def get_department_key(org_lv2):
    if "Engineering" in org_lv2 or "エンジニアリング" in org_lv2:
        return "Engineering"
    elif "HR" in org_lv2 or "人事" in org_lv2:
        return "HR"
    elif "Finance" in org_lv2 or "財務" in org_lv2:
        return "Finance"
    return "Sales"

def get_performance_level(engagement_score):
    for level, threshold in PERFORMANCE_THRESHOLDS.items():
        if engagement_score >= threshold:
            return level
    return "C"

def adjust_organization_by_position(employee, position_data, position):
    if position in position_data["hierarchy"]["executive"]:
        employee["org_lv2"] = None
        employee["org_lv3"] = None
        employee["org_lv4"] = None
    elif position in position_data["hierarchy"]["director"]:
        employee["org_lv3"] = None
        employee["org_lv4"] = None
    elif position in position_data["hierarchy"]["manager"]:
        employee["org_lv4"] = None
    return employee

def calculate_salary(base_range, position_hierarchy, position):
    """Calculate salary within the specified range based on position hierarchy"""
    min_salary, max_salary = base_range
    position_level = position_hierarchy.get(position, 1)
    
    # Calculate the percentage through the range based on position level
    min_level = min(position_hierarchy.values())
    max_level = max(position_hierarchy.values())
    level_range = max_level - min_level
    
    if level_range == 0:
        percentage = 0
    else:
        percentage = (position_level - min_level) / level_range
    
    # Calculate salary ensuring it stays within the specified range
    salary = min_salary + (max_salary - min_salary) * percentage
    return round(salary, -3)

def adjust_salary_by_performance(current_salary, performance):
    """Adjust salary based on performance evaluation"""
    adjustment_rate = SALARY_ADJUSTMENT_RATES.get(performance, 1.0)
    return round(current_salary * adjustment_rate, -3)

def update_performance_based_on_engagement(engagement_score):
    """Determine performance level based on engagement score"""
    if engagement_score >= 90:
        return "S"
    elif engagement_score >= 75:
        return "A"
    elif engagement_score >= 50:
        return "B"
    else:
        return "C"

def generate_employee_data():
    try:
        data = []
        current_date = datetime.now()
        base_employees = []

        position_hierarchy = {
            lang_data["positions"]["choices"][i]: (i + 1) / 2
            for i in range(len(lang_data["positions"]["choices"]))
        }

        position_to_grade = {
            lang_data["positions"]["choices"][i]: f"Lv{i+1}"
            for i in range(len(lang_data["positions"]["choices"]))
        }

        # 生成する従業員数を確保するためのカウンター
        employee_id_counter = 1
        attempts = 0
        max_attempts = employee_count * 2  # 無限ループ防止用の最大試行回数
        
        # Generate base employee data
        while len(base_employees) < employee_count and attempts < max_attempts:
            try:
                attempts += 1
                employee = {}
                
                # Basic information
                employee["emp_id"] = f"EMP{str(employee_id_counter).zfill(6)}"
                employee_id_counter += 1
                employee["name"] = fake.name()
                
                age = random.randint(age_range[0], age_range[1])
                birth_date = current_date - relativedelta(years=age)
                employee["birth_date"] = birth_date.strftime("%Y-%m-%d")
                
                employee["gender"] = random.choice(lang_data["genders"])
                
                # Organisation
                employee["org_lv1"] = random.choice(lang_data["organizations"]["org_lv1"])
                employee["org_lv2"] = random.choice(lang_data["organizations"]["org_lv2"])
                dept_key = get_department_key(employee["org_lv2"])
                
                org_lv3_options = lang_data["organizations"]["org_lv3"].get(dept_key, [])
                if not org_lv3_options:
                    # デフォルトの部門を使用
                    dept_key = "Sales"
                    org_lv3_options = lang_data["organizations"]["org_lv3"].get(dept_key, ["Default Department"])
                
                employee["org_lv3"] = random.choice(org_lv3_options)
                employee["org_lv4"] = random.choice(lang_data["organizations"]["org_lv4"])
                
                # Position and employment type
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
                
                # Adjust organisation based on position
                employee = adjust_organization_by_position(employee, lang_data["positions"], employee["position"])
                
                # Handle contract employees
                if employee["emp_type"] == lang_data["emp_types"]["choices"][1]:  # Contract
                    employee["position"] = lang_data["positions"]["choices"][0]  # Staff level
                
                # Handle temporary employees
                if employee["emp_type"] == lang_data["emp_types"]["choices"][2]:  # Temporary
                    employee = {**employee, **{
                        "salary": None,
                        "engagement_score": None,
                        "performance": None,
                        "address": None,
                        "job_grade": None,
                        "position": lang_data["positions"]["choices"][0]
                    }}
                else:
                    # Regular employee data
                    try:
                        employee["salary"] = calculate_salary(salary_range, position_hierarchy, employee["position"])
                    except Exception as e:
                        st.warning(f"給与計算中にエラーが発生しました: {str(e)}。デフォルト値を使用します。")
                        employee["salary"] = salary_range[0]  # デフォルト値を使用
                        
                    employee["engagement_score"] = round(random.uniform(14, 100), 0)
                    employee["performance"] = get_performance_level(employee["engagement_score"])
                    
                    employee["address"] = random.choice(
                        lang_data["cities"]["major"] if random.random() < 0.8 else lang_data["cities"]["other"]
                    )
                    
                    if employee["position"] in lang_data["positions"]["hierarchy"].get("executive", []):
                        employee["job_category"] = "Management"
                    else:
                        try:
                            employee["job_category"] = random.choice(lang_data["job_categories"].get(dept_key, ["Default"]))
                        except (KeyError, IndexError):
                            employee["job_category"] = "Default"
                    
                    employee["job_grade"] = position_to_grade.get(employee["position"], "Lv1")
                
                # Common fields for all employees
                employee["hire_date"] = (current_date - timedelta(days=random.randint(0, 365 * 20))).strftime("%Y-%m-%d")
                
                # 退職者は5%のみに設定し、退職していない社員は'2999-12-31'を設定
                if random.random() < 0.05:
                    employee["resign_date"] = (current_date - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
                else:
                    employee["resign_date"] = "2999-12-31"
                    
                employee["is_married"] = random.choice([True, False])
                
                base_employees.append(employee)
            except Exception as emp_error:
                st.warning(f"従業員データ生成中にエラーが発生しました（ID: EMP{str(employee_id_counter-1).zfill(6)}）: {str(emp_error)}")
                # continueせず、次の繰り返しで別の従業員を生成

        if len(base_employees) < employee_count:
            st.warning(f"要求された従業員数（{employee_count}）に対して、{len(base_employees)}名のデータのみ生成できました。")
            
        # Generate monthly data
        for month_offset in range(num_months):
            try:
                base_date = (current_date - timedelta(days=30 * (num_months - 1 - month_offset))).replace(day=1).strftime("%Y-%m-%d")
                
                for base_employee in base_employees:
                    try:
                        if base_employee["resign_date"] != "2999-12-31" and base_employee["resign_date"] and base_date > base_employee["resign_date"]:
                            continue

                        # Generate employee data for each month
                        employee = base_employee.copy()
                        employee["base_date"] = base_date

                        # Update performance and salary every 12 months
                        if month_offset % 12 == 0 and employee["resign_date"] != "2999-12-31":
                            if employee["emp_type"] != lang_data["emp_types"]["choices"][2]:  # Not temporary
                                try:
                                    # Update performance
                                    engagement_score = employee.get("engagement_score", random.uniform(0, 100))
                                    employee["performance"] = update_performance_based_on_engagement(engagement_score)

                                    # Update salary
                                    current_salary = employee.get("salary", 0)
                                    employee["salary"] = adjust_salary_by_performance(current_salary, employee["performance"])

                                    # Update the base data based on the above process
                                    base_employee.update({
                                        "performance": employee["performance"],
                                        "salary": employee["salary"]
                                    })
                                except Exception as update_error:
                                    st.warning(f"パフォーマンスと給与更新中にエラーが発生しました（ID: {employee.get('emp_id', 'Unknown')}）: {str(update_error)}")

                        # Update engagement score 
                        if employee["emp_type"] != lang_data["emp_types"]["choices"][2] and employee.get("engagement_score"):
                            if random.random() < 0.3:
                                try:
                                    employee["engagement_score"] = round(
                                        min(max(employee["engagement_score"] * random.uniform(0.9, 1.1), 0),100),
                                        0
                                    )
                                except Exception as score_error:
                                    st.warning(f"エンゲージメントスコア更新中にエラーが発生しました（ID: {employee.get('emp_id', 'Unknown')}）: {str(score_error)}")
                                    # エラー発生時はスコアを変更しない
                        
                        data.append(employee)
                    except Exception as monthly_emp_error:
                        st.warning(f"月次データ生成中にエラーが発生しました（ID: {base_employee.get('emp_id', 'Unknown')}）: {str(monthly_emp_error)}")
                        continue
            except Exception as month_error:
                st.warning(f"月次データセット生成中にエラーが発生しました（月オフセット: {month_offset}）: {str(month_error)}")
                continue
        
        if not data:
            st.error("データを生成できませんでした。パラメータを確認して再試行してください。")
            return pd.DataFrame()
            
        return pd.DataFrame(data)
        
    except Exception as e:
        st.error(f"データ生成中に重大なエラーが発生しました: {str(e)}")
        return pd.DataFrame()  # 空のDataFrameを返す

def main():
    try:
        setup_page()
        
        # Language selection
        global selected_language, t, lang_data
        selected_language = st.selectbox(
            "Language / 言語",
            list(LANGUAGE_DATA.keys())
        )
        
        t = TRANSLATIONS[selected_language]
        lang_data = LANGUAGE_DATA[selected_language]
        
        # Initialise Faker
        global fake
        try:
            fake = Faker({"English": "en_US", "Japanese": "ja_JP"}.get(selected_language, "en_US"))
        except Exception as fake_error:
            st.warning(f"Fakerの初期化中にエラーが発生しました: {str(fake_error)}。デフォルト言語（英語）を使用します。")
            fake = Faker("en_US")
        
        # UI Setup
        st.title(t["title"])
        st.markdown(t["description"])
        
        # Field descriptions
        try:
            fields = list(t["fields"].keys())
            descriptions = [t["fields"][field] for field in fields]
            df_desc = pd.DataFrame({"Field": fields, "Description": descriptions})
            st.subheader(t["field_descriptions"])
            st.table(df_desc)
        except Exception as desc_error:
            st.warning(f"フィールド説明の表示中にエラーが発生しました: {str(desc_error)}")
        
        # Sidebar configuration
        st.sidebar.header(t["config"])
        
        global employee_count, num_months, age_range, salary_range
        try:
            employee_count = st.sidebar.slider(t.get("num_employees", "Number of Employees"), 200, 500, 300)
            num_months = st.sidebar.slider(t.get("num_months", "Number of Months"), 1, 24, 1)
            
            st.sidebar.subheader(t.get("additional_params", "Additional Parameters"))
            age_range = st.sidebar.slider(t.get("age_range", "Age Range"), 18, 65, (25, 55))
            salary_range = st.sidebar.slider(t.get("salary_range", "Salary Range (JPY)"), 3000000, 30000000, (4000000, 10000000))
        except Exception as slider_error:
            st.error(f"スライダーの設定中にエラーが発生しました: {str(slider_error)}")
            # デフォルト値を設定
            employee_count = 300
            num_months = 1
            age_range = (25, 55)
            salary_range = (4000000, 10000000)
            
        # Generate data
        if st.button(t.get("generate_button", "Generate HR Data"), type="primary"):
            with st.spinner("データを生成中..."):
                try:
                    df = generate_employee_data()
                    if not df.empty:
                        st.subheader(t.get("data_preview", "Data Preview"))
                        st.dataframe(df.head(10))
                        
                        st.subheader(t.get("download_options", "Download Options"))
                        col1, col2, col3 = st.columns(3)
                        
                        try:
                            # Download options
                            csv = df.to_csv(index=False)
                            col1.download_button(t.get("download_csv", "Download CSV"), csv, "hr_data.csv", "text/csv")
                            
                            excel_buffer = BytesIO()
                            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                                df.to_excel(writer, index=False)
                            col2.download_button(t.get("download_excel", "Download Excel"), excel_buffer.getvalue(), "hr_data.xlsx")
                            
                            json = df.to_json(orient="records")
                            col3.download_button(t.get("download_json", "Download JSON"), json, "hr_data.json", "application/json")
                        except Exception as download_error:
                            st.error(f"ダウンロードオプションの準備中にエラーが発生しました: {str(download_error)}")
                except Exception as gen_error:
                    st.error(f"データ生成中に予期しないエラーが発生しました: {str(gen_error)}")
        
        # Footer
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"""
        ### {t.get("contact", "Contact")}
        - **email**: hrdata.generator@gmail.com
        - **X account**: @hrdata_gen
        """)
    
    except Exception as main_error:
        st.error(f"アプリケーションの実行中に重大なエラーが発生しました: {str(main_error)}")

if __name__ == "__main__":
    main()

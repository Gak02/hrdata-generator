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

def validate_employee_data(employee):
    """従業員データの整合性をチェックする"""
    try:
        # 日付の整合性チェック
        hire_date = datetime.strptime(employee["hire_date"], "%Y-%m-%d")
        resign_date = datetime.strptime(employee["resign_date"], "%Y-%m-%d") if employee["resign_date"] != "2999-12-31" else None
        birth_date = datetime.strptime(employee["birth_date"], "%Y-%m-%d")
        current_date = datetime.now()

        # 入社日は現在日以前である必要がある
        if hire_date > current_date:
            return False, "入社日が現在日より未来です"

        # 退職日は入社日以降である必要がある
        if resign_date and resign_date < hire_date:
            return False, "退職日が入社日より前です"

        # 年齢チェック
        age = (current_date - birth_date).days / 365.25
        if not (age_range[0] <= age <= age_range[1]):
            return False, f"年齢が範囲外です: {age:.1f}歳"

        # 給与チェック
        if employee["salary"] is not None:
            if not (salary_range[0] <= employee["salary"] <= salary_range[1]):
                return False, f"給与が範囲外です: {employee['salary']}円"

        # エンゲージメントスコアチェック
        if employee["engagement_score"] is not None:
            if not (0 <= employee["engagement_score"] <= 100):
                return False, f"エンゲージメントスコアが範囲外です: {employee['engagement_score']}"

        # 組織階層の整合性チェック
        if employee["position"] in lang_data["positions"]["hierarchy"]["executive"]:
            if any([employee["org_lv2"], employee["org_lv3"], employee["org_lv4"]]):
                return False, "役員の組織階層が不適切です"
        elif employee["position"] in lang_data["positions"]["hierarchy"]["director"]:
            if any([employee["org_lv3"], employee["org_lv4"]]):
                return False, "部長の組織階層が不適切です"
        elif employee["position"] in lang_data["positions"]["hierarchy"]["manager"]:
            if employee["org_lv4"]:
                return False, "マネージャーの組織階層が不適切です"

        return True, "OK"
    except Exception as e:
        return False, f"データ検証中にエラーが発生しました: {str(e)}"

def update_organization_hierarchy(employee, position):
    """役職に応じて組織階層を更新する"""
    try:
        if position in lang_data["positions"]["hierarchy"]["executive"]:
            employee["org_lv2"] = None
            employee["org_lv3"] = None
            employee["org_lv4"] = None
        elif position in lang_data["positions"]["hierarchy"]["director"]:
            employee["org_lv3"] = None
            employee["org_lv4"] = None
        elif position in lang_data["positions"]["hierarchy"]["manager"]:
            employee["org_lv4"] = None
        return employee
    except Exception as e:
        st.warning(f"組織階層の更新中にエラーが発生しました: {str(e)}")
        return employee

def update_resign_dates(df, current_date):
    """退職した従業員の退職日を更新する"""
    try:
        # 従業員IDごとにグループ化
        grouped = df.groupby('emp_id')
        
        # 各従業員のデータを処理
        for emp_id, group in grouped:
            # 退職フラグを確認（退職月のデータが存在しない場合）
            if len(group) < len(df['base_date'].unique()):
                # 最後のデータの日付を取得
                last_date = group['base_date'].max()
                last_date_dt = datetime.strptime(last_date, "%Y-%m-%d")
                
                # 退職日を当月の末日に設定
                resign_date = (last_date_dt + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")
                
                # 退職日を更新
                df.loc[df['emp_id'] == emp_id, 'resign_date'] = resign_date
        
        return df
    except Exception as e:
        st.warning(f"退職日の更新中にエラーが発生しました: {str(e)}")
        return df

def generate_employee_data():
    try:
        data = []
        current_date = datetime.now()
        base_employees = []

        # より現実的な役職階層を設定
        position_hierarchy = {
            lang_data["positions"]["choices"][i]: 1 + (i * 0.5)  # より現実的な階層差
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
                # 年齢レンジから生年月日の範囲を計算し、完全ランダムな日付を生成
                from_date = current_date - relativedelta(years=age_range[1])
                to_date = current_date - relativedelta(years=age_range[0])
                birth_date = fake.date_between_dates(date_start=from_date, date_end=to_date)
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
                    # 契約社員の給与は正社員の80%を基本とするが、最低給与範囲を下回らないようにする
                    base_salary = calculate_salary(salary_range, position_hierarchy, employee["position"])
                    contract_salary = round(base_salary * 0.8, -3)
                    # 最低給与範囲を下回らないように調整
                    employee["salary"] = max(contract_salary, salary_range[0])
                    
                    # 契約社員にも必要なデータを生成
                    engagement_score = np.random.normal(70, 15)
                    engagement_score = max(0, min(100, round(engagement_score)))
                    employee["engagement_score"] = engagement_score
                    employee["performance"] = get_performance_level(employee["engagement_score"])
                    
                    employee["address"] = random.choice(
                        lang_data["cities"]["major"] if random.random() < 0.8 else lang_data["cities"]["other"]
                    )
                    
                    try:
                        employee["job_category"] = random.choice(lang_data["job_categories"].get(dept_key, ["Default"]))
                    except (KeyError, IndexError):
                        employee["job_category"] = "Default"
                    
                    employee["job_grade"] = position_to_grade.get(employee["position"], "Lv1")
                elif employee["emp_type"] == lang_data["emp_types"]["choices"][2]:  # Temporary
                    # 派遣社員は基本情報のみを生成
                    employee["position"] = lang_data["positions"]["choices"][0]  # Staff level
                    employee["salary"] = None
                    employee["engagement_score"] = None
                    employee["performance"] = None
                    employee["address"] = None
                    employee["job_category"] = None
                    employee["job_grade"] = None
                else:
                    # Regular employee data
                    try:
                        employee["salary"] = calculate_salary(salary_range, position_hierarchy, employee["position"])
                    except Exception as e:
                        st.warning(f"給与計算中にエラーが発生しました: {str(e)}。デフォルト値を使用します。")
                        employee["salary"] = salary_range[0]  # デフォルト値を使用
                        
                    # 正規分布を使用してengagement_scoreを生成（平均70、標準偏差15）
                    engagement_score = np.random.normal(70, 15)
                    # 0-100の範囲に収める
                    engagement_score = max(0, min(100, round(engagement_score)))
                    employee["engagement_score"] = engagement_score
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
                hire_date = (current_date - timedelta(days=random.randint(0, 365 * 20))).strftime("%Y-%m-%d")
                employee["hire_date"] = hire_date
                
                # 初期状態では全員が在籍中とする
                employee["resign_date"] = "2999-12-31"
                    
                employee["is_married"] = random.choice([True, False])
                
                # データの整合性チェック
                is_valid, error_message = validate_employee_data(employee)
                if not is_valid:
                    st.warning(f"従業員データの整合性チェックに失敗しました（ID: {employee['emp_id']}）: {error_message}")
                    continue
                
                base_employees.append(employee)
            except Exception as emp_error:
                st.warning(f"従業員データ生成中にエラーが発生しました（ID: EMP{str(employee_id_counter-1).zfill(6)}）: {str(emp_error)}")
                # continueせず、次の繰り返しで別の従業員を生成

        if len(base_employees) < employee_count:
            st.warning(f"要求された従業員数（{employee_count}）に対して、{len(base_employees)}名のデータのみ生成できました。")
            
        # Generate monthly data
        for month_offset in range(num_months):
            try:
                # より正確な月単位の計算を行う
                base_date = (current_date - relativedelta(months=(num_months - 1 - month_offset))).replace(day=1).strftime("%Y-%m-%d")
                
                # 各従業員のデータを生成
                for base_employee in base_employees:
                    try:
                        # 退職後のデータは生成しない
                        if base_employee["resign_date"] != "2999-12-31" and base_date > base_employee["resign_date"]:
                            continue

                        # Generate employee data for each month
                        employee = base_employee.copy()
                        employee["base_date"] = base_date

                        # 退職処理（年間10%の退職率を実現）
                        if base_employee["resign_date"] == "2999-12-31" and base_employee["emp_type"] != lang_data["emp_types"]["choices"][2]:  # 派遣社員以外
                            # 入社から1年以上経過している場合のみ退職の可能性を考慮
                            hire_date_dt = datetime.strptime(base_employee["hire_date"], "%Y-%m-%d")
                            base_date_dt = datetime.strptime(base_date, "%Y-%m-%d")
                            years_of_service = (base_date_dt - hire_date_dt).days / 365.25
                            
                            if years_of_service >= 1:
                                # 月次の退職確率を計算（年間10%を月次に換算）
                                monthly_resign_probability = 1 - (1 - 0.10) ** (1/12)
                                if random.random() < monthly_resign_probability:
                                    # 退職日を当月の末日に設定
                                    resign_date = (base_date_dt + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")
                                    # 基本データを更新
                                    base_employee["resign_date"] = resign_date
                                    # 月次データも更新
                                    employee["resign_date"] = resign_date
                                    # 退職月のデータは生成しない
                                    continue

                        # 役職変更の可能性を考慮（年1回、5%の確率で変更）
                        if month_offset % 12 == 0 and random.random() < 0.05 and employee["emp_type"] != lang_data["emp_types"]["choices"][2]:  # 派遣社員以外
                            try:
                                # 現在の役職のインデックスを取得
                                current_position_index = lang_data["positions"]["choices"].index(employee["position"])
                                # 1つ上の役職に昇進（最上位の場合は変更なし）
                                if current_position_index < len(lang_data["positions"]["choices"]) - 1:
                                    new_position = lang_data["positions"]["choices"][current_position_index + 1]
                                    employee["position"] = new_position
                                    # 組織階層を更新
                                    employee = update_organization_hierarchy(employee, new_position)
                                    # 給与を更新
                                    if employee["emp_type"] == lang_data["emp_types"]["choices"][1]:  # 契約社員
                                        base_salary = calculate_salary(salary_range, position_hierarchy, new_position)
                                        contract_salary = round(base_salary * 0.8, -3)
                                        # 最低給与範囲を下回らないように調整
                                        employee["salary"] = max(contract_salary, salary_range[0])
                                    else:  # 正社員
                                        employee["salary"] = calculate_salary(salary_range, position_hierarchy, new_position)
                                    # 基本データも更新
                                    base_employee.update({
                                        "position": new_position,
                                        "org_lv2": employee["org_lv2"],
                                        "org_lv3": employee["org_lv3"],
                                        "org_lv4": employee["org_lv4"],
                                        "salary": employee["salary"]
                                    })
                            except Exception as position_error:
                                st.warning(f"役職更新中にエラーが発生しました（ID: {employee.get('emp_id', 'Unknown')}）: {str(position_error)}")

                        # Update performance and salary every 12 months
                        if month_offset % 12 == 0:
                            # 入社月からの12ヶ月で評価
                            hire_month = datetime.strptime(employee["hire_date"], "%Y-%m-%d").month
                            current_month = datetime.strptime(base_date, "%Y-%m-%d").month
                            
                            # 退職月は評価を行わない
                            if current_month == hire_month and base_date < employee["resign_date"]:
                                # 派遣社員以外（正社員と契約社員）にパフォーマンス評価を実施
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
                        # 派遣社員以外（正社員と契約社員）にエンゲージメントスコアを更新
                        if employee["emp_type"] != lang_data["emp_types"]["choices"][2] and employee.get("engagement_score"):
                            # 退職月以降は更新しない
                            if base_date < employee["resign_date"]:
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
        
        # データフレームを作成
        df = pd.DataFrame(data)
        
        # 退職日の更新を実行
        df = update_resign_dates(df, current_date)
            
        return df
        
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

"""Constants and configuration data for HR Data Generator."""

MIN_EMPLOYEES = 100
MAX_EMPLOYEES = 500
DEFAULT_EMPLOYEES = 300

PERFORMANCE_THRESHOLDS = {
    "S": 90,
    "A": 75,
    "B": 50,
    "C": 0,
}

SALARY_ADJUSTMENT_RATES = {
    "S": 1.20,
    "A": 1.10,
    "B": 1.05,
    "C": 0.97,
}

JOB_GRADE_SALARY_BANDS = {
    # grade: (salary_range内の下限%, 上限%)
    "Lv1": (0.00, 0.15),   # 一般社員 / Staff
    "Lv2": (0.10, 0.30),   # チームリーダー / Team Lead
    "Lv3": (0.25, 0.50),   # マネージャー / Manager
    "Lv4": (0.45, 0.70),   # 部長 / General Manager
    "Lv5": (0.65, 0.85),   # 執行役員 / VP
    "Lv6": (0.80, 1.00),   # 取締役 / C-level
}

FORCED_PERFORMANCE_DISTRIBUTION = {
    "S": 0.05,
    "A": 0.20,
    "B": 0.60,
    "C": 0.15,
}

# Department distribution weights (org_lv2)
DEPARTMENT_WEIGHTS = {
    "English": {
        "Sales & Marketing": 40,
        "Engineering": 30,
        "HR": 15,
        "Finance": 15,
    },
    "Japanese": {
        "営業・マーケティング": 40,
        "エンジニアリング": 30,
        "人事": 15,
        "財務": 15,
    },
}

# Resignation reasons by language
RESIGNATION_REASONS = {
    "English": [
        "Voluntary - Career Change",
        "Voluntary - Personal Reasons",
        "Voluntary - Relocation",
        "Contract Expiry",
        "Retirement",
        "Involuntary - Restructuring",
    ],
    "Japanese": [
        "自己都合 - キャリアチェンジ",
        "自己都合 - 個人的理由",
        "自己都合 - 転居",
        "契約満了",
        "定年退職",
        "会社都合 - 組織再編",
    ],
}

# Hire month weights by language (1=Jan .. 12=Dec)
HIRE_MONTH_WEIGHTS = {
    "English": {
        1: 20, 2: 8, 3: 8, 4: 8, 5: 8, 6: 10,
        7: 5, 8: 5, 9: 15, 10: 8, 11: 3, 12: 2,
    },
    "Japanese": {
        1: 5, 2: 3, 3: 5, 4: 40, 5: 5, 6: 5,
        7: 5, 8: 3, 9: 8, 10: 10, 11: 5, 12: 6,
    },
}

# Age-based position weight adjustments
# Each entry: (age_min, age_max) -> multiplier per position index
# Position order: Staff(0), Team Lead(1), Manager(2), Gen Mgr(3), VP(4), C-level(5)
AGE_POSITION_WEIGHT_MODIFIERS = {
    (0, 29): [3.0, 1.0, 0.1, 0.0, 0.0, 0.0],
    (30, 39): [1.5, 2.0, 1.5, 0.5, 0.1, 0.0],
    (40, 49): [0.8, 1.5, 2.0, 2.0, 1.0, 0.5],
    (50, 99): [0.5, 1.0, 1.5, 2.5, 2.0, 2.0],
}

# Marriage rate by age bracket
MARRIAGE_RATE_BY_AGE = {
    (0, 24): 0.10,
    (25, 29): 0.25,
    (30, 34): 0.50,
    (35, 39): 0.65,
    (40, 44): 0.75,
    (45, 99): 0.80,
}

LANGUAGE_DATA = {
    "English": {
        "organizations": {
            "org_lv1": ["Hogehoge inc."],
            "org_lv2": ["Sales & Marketing", "Engineering", "HR", "Finance"],
            "org_lv3": {
                "Sales": ["Global Sales", "Regional Sales", "Sales Operations", "Business Development"],
                "Engineering": ["Software Development", "Cloud Infrastructure", "Data Engineering", "Product Development"],
                "HR": ["Talent Acquisition", "People Operations", "Learning & Development", "HR Operations"],
                "Finance": ["Financial Planning", "Accounting", "Treasury", "Internal Audit"],
            },
            "org_lv4": ["Team Alpha", "Team Beta", "Team Gamma", "Team Delta", "Team Epsilon"],
        },
        "positions": {
            "choices": ["Staff", "Team Lead", "Manager", "General Manager", "VP", "C-level"],
            "weights": [50, 30, 10, 5, 3, 2],
            "hierarchy": {
                "executive": ["VP", "C-level"],
                "director": ["General Manager"],
                "manager": ["Manager"],
            },
        },
        "emp_types": {
            "choices": ["Full-time", "Contract", "Temporary"],
            "weights": [70, 20, 10],
        },
        "job_categories": {
            "Sales": ["Sales Representative", "Account Manager", "Sales Operations", "Business Development"],
            "Engineering": ["Software Engineer", "Data Engineer", "Cloud Architect", "DevOps Engineer"],
            "HR": ["HR Specialist", "Recruiter", "HR Operations", "Training Specialist"],
            "Finance": ["Financial Analyst", "Accountant", "Treasury Analyst", "Auditor"],
        },
        "genders": {
            "choices": ["Male", "Female", "Other"],
            "weights": [70, 28, 2],
        },
        "cities": {
            "major": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
            "other": ["Seattle", "Boston", "Denver", "Austin", "Portland"],
        },
        "faker_locale": "en_US",
    },
    "Japanese": {
        "organizations": {
            "org_lv1": ["株式会社hogehoge"],
            "org_lv2": ["営業・マーケティング", "エンジニアリング", "人事", "財務"],
            "org_lv3": {
                "Sales": ["グローバル営業", "国内営業", "営業管理", "事業開発"],
                "Engineering": ["ソフトウェア開発", "クラウドインフラ", "データエンジニアリング", "製品開発"],
                "HR": ["採用", "人事オペレーション", "人材開発", "労務管理"],
                "Finance": ["経営企画", "経理", "財務", "内部監査"],
            },
            "org_lv4": ["第一チーム", "第二チーム", "第三チーム", "第四チーム", "第五チーム"],
        },
        "positions": {
            "choices": ["一般社員", "チームリーダー", "マネージャー", "部長", "執行役員", "取締役"],
            "weights": [50, 30, 10, 5, 3, 2],
            "hierarchy": {
                "executive": ["執行役員", "取締役"],
                "director": ["部長"],
                "manager": ["マネージャー"],
            },
        },
        "emp_types": {
            "choices": ["正社員", "契約社員", "派遣社員"],
            "weights": [70, 20, 10],
        },
        "job_categories": {
            "Sales": ["営業担当", "アカウントマネージャー", "営業管理", "事業開発"],
            "Engineering": ["ソフトウェアエンジニア", "データエンジニア", "クラウドアーキテクト", "DevOpsエンジニア"],
            "HR": ["人事担当", "採用担当", "人事業務", "研修担当"],
            "Finance": ["財務アナリスト", "経理担当", "財務担当", "監査担当"],
        },
        "genders": {
            "choices": ["男性", "女性", "その他"],
            "weights": [70, 28, 2],
        },
        "cities": {
            "major": ["東京", "横浜", "大阪", "名古屋", "福岡"],
            "other": ["札幌", "仙台", "広島", "神戸", "京都"],
        },
        "faker_locale": "ja_JP",
    },
}

TRANSLATIONS = {
    "English": {
        "title": "HR Data Generator",
        "description": (
            "This application generates sample HR data for multiple months with realistic employee information.\n"
            "You can customise various parameters and download the generated dataset in multiple formats."
        ),
        "config": "Configuration",
        "language": "Select Language",
        "num_employees": "Number of Employees",
        "num_months": "Number of Months",
        "additional_params": "Additional Parameters",
        "age_range": "Age Range",
        "salary_range": "Salary Range",
        "include_concurrent": "Include Concurrent Positions",
        "concurrent_tooltip": "Some employees will belong to multiple departments",
        "generate_button": "Generate HR Data",
        "data_preview": "Data Preview",
        "charts_title": "Data Visualization",
        "chart_salary_box": "Salary Distribution by Position",
        "chart_org_bar": "Headcount by Department",
        "chart_gender_pie": "Gender Distribution",
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
            "Salary": "Annual salary *Update every 12 months based on performance",
            "Hire Date": "Employment start date",
            "Resign Date": "Employment end date (if applicable)",
            "Engagement Score": "Employee engagement score",
            "Performance": "Annual performance result *Update every 12 months",
            "Marital Status": "Whether the employee is married",
            "Address": "Employee's address",
            "Job Category": "Functional or professional category for the job",
            "Job Grade": "Grade or level of the job within the company",
            "Base date": "Date at when data is generated",
        },
    },
    "Japanese": {
        "title": "人事データ生成ツール",
        "description": (
            "このアプリケーションは、1~24ヶ月分の現実的な従業員情報を生成します。\n"
            "さまざまなパラメータをカスタマイズして、生成したデータセットを複数の形式でダウンロードできます。"
        ),
        "config": "設定",
        "language": "言語選択",
        "num_employees": "従業員数",
        "num_months": "生成月数",
        "additional_params": "追加パラメータ",
        "age_range": "年齢範囲",
        "salary_range": "給与範囲（円）",
        "include_concurrent": "兼務レコードを含める",
        "concurrent_tooltip": "一部の従業員が複数の部門に所属するレコードを生成します",
        "generate_button": "データを生成",
        "data_preview": "データプレビュー",
        "charts_title": "データ可視化",
        "chart_salary_box": "役職別給与分布",
        "chart_org_bar": "部門別人数",
        "chart_gender_pie": "性別構成",
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
            "Base date": "基準日",
        },
    },
}

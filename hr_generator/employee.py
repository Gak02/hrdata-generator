"""Pure functions for creating and validating individual employees."""
import random
from datetime import datetime, timedelta

import numpy as np
from dateutil.relativedelta import relativedelta

from hr_generator.config import (
    PERFORMANCE_THRESHOLDS,
    SALARY_ADJUSTMENT_RATES,
    JOB_GRADE_SALARY_BANDS,
    AGE_POSITION_WEIGHT_MODIFIERS,
    MARRIAGE_RATE_BY_AGE,
    DEPARTMENT_WEIGHTS,
    HIRE_MONTH_WEIGHTS,
    FORCED_PERFORMANCE_DISTRIBUTION,
)


def get_department_key(org_lv2):
    """Map org_lv2 name to department key for org_lv3 lookup."""
    if "Engineering" in org_lv2 or "エンジニアリング" in org_lv2:
        return "Engineering"
    elif "HR" in org_lv2 or "人事" in org_lv2:
        return "HR"
    elif "Finance" in org_lv2 or "財務" in org_lv2:
        return "Finance"
    return "Sales"


def get_performance_level(engagement_score):
    """Map engagement score to performance level (S/A/B/C)."""
    for level, threshold in PERFORMANCE_THRESHOLDS.items():
        if engagement_score >= threshold:
            return level
    return "C"


def assign_forced_performance(employees):
    """Assign performance ratings following a forced distribution (C4).

    Only applies to employees with non-null engagement_score.
    Employees are ranked by engagement_score and then assigned ratings
    according to FORCED_PERFORMANCE_DISTRIBUTION.
    """
    # Separate employees with and without scores
    scoreable = [e for e in employees if e.get("engagement_score") is not None]
    if not scoreable:
        return

    # Sort by engagement_score descending
    scoreable.sort(key=lambda e: e["engagement_score"], reverse=True)
    n = len(scoreable)

    # Calculate cutoff indices
    s_end = round(n * FORCED_PERFORMANCE_DISTRIBUTION["S"])
    a_end = s_end + round(n * FORCED_PERFORMANCE_DISTRIBUTION["A"])
    b_end = a_end + round(n * FORCED_PERFORMANCE_DISTRIBUTION["B"])

    for i, emp in enumerate(scoreable):
        if i < s_end:
            emp["performance"] = "S"
        elif i < a_end:
            emp["performance"] = "A"
        elif i < b_end:
            emp["performance"] = "B"
        else:
            emp["performance"] = "C"


def get_age_adjusted_position_weights(age, lang_data):
    """Return position weights adjusted for employee age (A1).

    Younger employees get higher weight for junior roles;
    older employees get higher weight for senior roles.
    """
    base_weights = lang_data["positions"]["weights"]
    modifiers = [1.0] * len(base_weights)

    for (age_min, age_max), mods in AGE_POSITION_WEIGHT_MODIFIERS.items():
        if age_min <= age <= age_max:
            modifiers = mods
            break

    adjusted = [
        max(base_weights[i] * modifiers[i], 0.01)
        for i in range(len(base_weights))
    ]
    return adjusted


def adjust_organization_by_position(employee, position_data, position):
    """Nullify org levels based on position hierarchy."""
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


def calculate_salary(base_range, job_grade, age_factor=0.5):
    """Calculate salary within the job grade's band with random variation.

    Args:
        base_range: (min_salary, max_salary) tuple from config.
        job_grade: Grade string like "Lv1" ~ "Lv6".
        age_factor: 0.0 (youngest) to 1.0 (oldest) within the grade band.
                    Used to bias older employees toward the upper end (C3).

    Returns:
        Salary rounded to nearest 1000.
    """
    min_salary, max_salary = base_range
    salary_span = max_salary - min_salary

    band_low, band_high = JOB_GRADE_SALARY_BANDS[job_grade]
    grade_min = min_salary + salary_span * band_low
    grade_max = min_salary + salary_span * band_high

    # Blend age_factor with randomness: 60% age influence, 40% random
    random_component = random.random()
    blended = age_factor * 0.6 + random_component * 0.4

    salary = grade_min + (grade_max - grade_min) * blended
    return round(salary, -3)


def adjust_salary_by_performance(current_salary, performance):
    """Adjust salary based on performance evaluation."""
    adjustment_rate = SALARY_ADJUSTMENT_RATES.get(performance, 1.0)
    return round(current_salary * adjustment_rate, -3)


def _build_position_hierarchy(lang_data):
    """Build position -> numeric level mapping."""
    return {
        lang_data["positions"]["choices"][i]: 1 + (i * 0.5)
        for i in range(len(lang_data["positions"]["choices"]))
    }


def _build_position_to_grade(lang_data):
    """Build position -> grade string mapping."""
    return {
        lang_data["positions"]["choices"][i]: f"Lv{i+1}"
        for i in range(len(lang_data["positions"]["choices"]))
    }


def _generate_hire_date(config, lang_data, current_date, position_index):
    """Generate a hire date with seasonality (C2) and tenure-position correlation (A2).

    Args:
        config: GeneratorConfig.
        lang_data: Language-specific data.
        current_date: Current datetime.
        position_index: 0 (Staff) to 5 (C-level).

    Returns:
        hire_date as datetime.
    """
    language = config.language

    # A2: Senior positions get longer tenure
    # Staff: 0-10 years, Team Lead: 2-12, Manager: 5-15, GM: 8-18, VP: 10-20, C-level: 12-20
    min_tenure_years = min(position_index * 2, 12)
    max_tenure_years = min(10 + position_index * 2, 20)
    tenure_days = random.randint(min_tenure_years * 365, max_tenure_years * 365)

    # C2: Hire month seasonality
    month_weights = HIRE_MONTH_WEIGHTS.get(language, HIRE_MONTH_WEIGHTS["English"])
    months = list(month_weights.keys())
    weights = list(month_weights.values())
    hire_month = random.choices(months, weights=weights, k=1)[0]

    # Build the hire date
    base_date = current_date - timedelta(days=tenure_days)
    # Replace month with seasonal month, keeping the year
    try:
        hire_date = base_date.replace(month=hire_month, day=1)
    except ValueError:
        hire_date = base_date.replace(month=hire_month, day=1)

    # Ensure not in the future
    if hire_date > current_date:
        hire_date = hire_date.replace(year=hire_date.year - 1)

    return hire_date


def _generate_new_grad_hire_date(current_date):
    """Generate April 1st hire date for Japanese new graduates (C5)."""
    # Pick a random year in the past 0-3 years
    years_ago = random.randint(0, 3)
    year = current_date.year - years_ago
    hire_date = datetime(year, 4, 1)
    if hire_date > current_date:
        hire_date = datetime(year - 1, 4, 1)
    return hire_date


def create_employee(config, lang_data, fake, employee_id):
    """Create a single employee dict. Always returns a valid employee."""
    position_to_grade = _build_position_to_grade(lang_data)
    current_date = datetime.now()

    employee = {}

    # Basic information
    employee["emp_id"] = f"EMP{str(employee_id).zfill(6)}"
    employee["name"] = fake.name()

    # Birth date from age range
    from_date = current_date - relativedelta(years=config.age_range[1])
    to_date = current_date - relativedelta(years=config.age_range[0])
    birth_date = fake.date_between_dates(date_start=from_date, date_end=to_date)
    employee["birth_date"] = birth_date.strftime("%Y-%m-%d")

    # Calculate age for age-dependent logic
    age = (current_date.date() - birth_date).days / 365.25

    employee["gender"] = random.choices(
        lang_data["genders"]["choices"],
        weights=lang_data["genders"]["weights"],
        k=1,
    )[0]

    # C1: Department distribution with weights
    language = config.language
    dept_weights = DEPARTMENT_WEIGHTS.get(language, {})
    org_lv2_options = lang_data["organizations"]["org_lv2"]
    if dept_weights:
        dept_weight_list = [dept_weights.get(d, 10) for d in org_lv2_options]
        employee["org_lv2"] = random.choices(
            org_lv2_options, weights=dept_weight_list, k=1
        )[0]
    else:
        employee["org_lv2"] = random.choice(org_lv2_options)

    employee["org_lv1"] = random.choice(lang_data["organizations"]["org_lv1"])
    dept_key = get_department_key(employee["org_lv2"])

    org_lv3_options = lang_data["organizations"]["org_lv3"].get(dept_key, [])
    if not org_lv3_options:
        dept_key = "Sales"
        org_lv3_options = lang_data["organizations"]["org_lv3"].get(dept_key, ["Default Department"])

    employee["org_lv3"] = random.choice(org_lv3_options)
    employee["org_lv4"] = random.choice(lang_data["organizations"]["org_lv4"])

    # A1: Age-adjusted position weights
    age_adjusted_weights = get_age_adjusted_position_weights(age, lang_data)
    employee["position"] = random.choices(
        lang_data["positions"]["choices"],
        weights=age_adjusted_weights,
        k=1,
    )[0]

    employee["emp_type"] = random.choices(
        lang_data["emp_types"]["choices"],
        weights=lang_data["emp_types"]["weights"],
        k=1,
    )[0]

    # Adjust organisation based on position
    employee = adjust_organization_by_position(
        employee, lang_data["positions"], employee["position"]
    )

    # Employment-type specific logic
    emp_type_choices = lang_data["emp_types"]["choices"]
    is_contract = employee["emp_type"] == emp_type_choices[1]
    is_temporary = employee["emp_type"] == emp_type_choices[2]

    # Determine job_grade early (needed for salary calculation)
    if is_temporary:
        job_grade = None
    else:
        job_grade = position_to_grade.get(employee["position"], "Lv1")

    # C3: Age factor for salary calculation (older = higher within band)
    age_min, age_max = config.age_range
    if age_max > age_min:
        age_factor = min(max((age - age_min) / (age_max - age_min), 0.0), 1.0)
    else:
        age_factor = 0.5

    if is_contract:
        employee["position"] = lang_data["positions"]["choices"][0]  # Staff level
        job_grade = "Lv1"  # Contract employees are always Lv1
        base_salary = calculate_salary(config.salary_range, job_grade, age_factor)
        contract_salary = round(base_salary * 0.8, -3)
        employee["salary"] = max(contract_salary, config.salary_range[0])
    elif is_temporary:
        employee["position"] = lang_data["positions"]["choices"][0]  # Staff level
        employee["salary"] = None
    else:
        employee["salary"] = calculate_salary(config.salary_range, job_grade, age_factor)

    # Engagement and performance (initial; C4 forced distribution applied later in generator)
    if is_temporary:
        employee["engagement_score"] = None
        employee["performance"] = None
    else:
        engagement_score = np.random.normal(70, 15)
        engagement_score = max(0, min(100, round(engagement_score)))
        employee["engagement_score"] = engagement_score
        # Temporary performance; will be overwritten by assign_forced_performance
        employee["performance"] = get_performance_level(engagement_score)

    # Address
    if is_temporary:
        employee["address"] = None
    else:
        employee["address"] = random.choice(
            lang_data["cities"]["major"] if random.random() < 0.8 else lang_data["cities"]["other"]
        )

    # Job category
    if is_temporary:
        employee["job_category"] = None
    elif employee["position"] in lang_data["positions"]["hierarchy"].get("executive", []):
        employee["job_category"] = "Management"
    else:
        employee["job_category"] = random.choice(
            lang_data["job_categories"].get(dept_key, ["Default"])
        )

    # Job grade (already computed above for salary calculation)
    employee["job_grade"] = job_grade

    # A2 + C2 + C5: Hire date with tenure-position correlation and seasonality
    position_index = lang_data["positions"]["choices"].index(employee["position"])

    # C5: Japanese new graduates (young employees, age < 26)
    is_japanese = language == "Japanese"
    is_new_grad_candidate = is_japanese and age < 26 and not is_contract and not is_temporary

    if is_new_grad_candidate and random.random() < 0.70:
        # 70% of young Japanese employees are new grads
        hire_date = _generate_new_grad_hire_date(current_date)
    else:
        hire_date = _generate_hire_date(config, lang_data, current_date, position_index)

    employee["hire_date"] = hire_date.strftime("%Y-%m-%d")
    employee["resign_date"] = "2999-12-31"

    # A5: Contract end date
    if is_contract:
        contract_years = random.randint(1, 3)
        contract_end = hire_date + relativedelta(years=contract_years)
        employee["contract_end_date"] = contract_end.strftime("%Y-%m-%d")
    else:
        employee["contract_end_date"] = None

    # A7: Marriage rate by age
    married_rate = 0.5  # default
    for (age_min_bracket, age_max_bracket), rate in MARRIAGE_RATE_BY_AGE.items():
        if age_min_bracket <= age <= age_max_bracket:
            married_rate = rate
            break
    employee["is_married"] = random.random() < married_rate

    # A6: Resignation reason (None for active employees)
    employee["resignation_reason"] = None

    return employee


def validate_employee(employee, age_range, salary_range, lang_data):
    """Validate employee data consistency. Returns (is_valid, message)."""
    # Date consistency
    hire_date = datetime.strptime(employee["hire_date"], "%Y-%m-%d")
    birth_date = datetime.strptime(employee["birth_date"], "%Y-%m-%d")
    current_date = datetime.now()

    if hire_date > current_date:
        return False, "Hire date is in the future"

    resign_date_str = employee["resign_date"]
    if resign_date_str != "2999-12-31":
        resign_date = datetime.strptime(resign_date_str, "%Y-%m-%d")
        if resign_date < hire_date:
            return False, "Resign date before hire date"

    # Age check
    age = (current_date - birth_date).days / 365.25
    if not (age_range[0] <= age <= age_range[1] + 1):
        return False, f"Age out of range: {age:.1f}"

    # Salary check
    if employee["salary"] is not None:
        if not (salary_range[0] <= employee["salary"] <= salary_range[1]):
            return False, f"Salary out of range: {employee['salary']}"

    # Engagement score check
    if employee["engagement_score"] is not None:
        if not (0 <= employee["engagement_score"] <= 100):
            return False, f"Engagement score out of range: {employee['engagement_score']}"

    # Org hierarchy consistency
    position = employee["position"]
    positions = lang_data["positions"]
    if position in positions["hierarchy"]["executive"]:
        if any([employee["org_lv2"], employee["org_lv3"], employee["org_lv4"]]):
            return False, "Executive should not have lower org levels"
    elif position in positions["hierarchy"]["director"]:
        if any([employee["org_lv3"], employee["org_lv4"]]):
            return False, "Director should not have org_lv3/lv4"
    elif position in positions["hierarchy"]["manager"]:
        if employee["org_lv4"]:
            return False, "Manager should not have org_lv4"

    return True, "OK"

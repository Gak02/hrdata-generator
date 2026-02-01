"""Pure functions for creating and validating individual employees."""
import random
from datetime import datetime, timedelta

import numpy as np
from dateutil.relativedelta import relativedelta

from hr_generator.config import PERFORMANCE_THRESHOLDS, SALARY_ADJUSTMENT_RATES


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


def calculate_salary(base_range, position_hierarchy, position):
    """Calculate salary within the specified range based on position level."""
    min_salary, max_salary = base_range
    position_level = position_hierarchy.get(position, 1)

    min_level = min(position_hierarchy.values())
    max_level = max(position_hierarchy.values())
    level_range = max_level - min_level

    if level_range == 0:
        percentage = 0
    else:
        percentage = (position_level - min_level) / level_range

    salary = min_salary + (max_salary - min_salary) * percentage
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


def create_employee(config, lang_data, fake, employee_id):
    """Create a single employee dict. Always returns a valid employee."""
    position_hierarchy = _build_position_hierarchy(lang_data)
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

    employee["gender"] = random.choice(lang_data["genders"])

    # Organisation
    employee["org_lv1"] = random.choice(lang_data["organizations"]["org_lv1"])
    employee["org_lv2"] = random.choice(lang_data["organizations"]["org_lv2"])
    dept_key = get_department_key(employee["org_lv2"])

    org_lv3_options = lang_data["organizations"]["org_lv3"].get(dept_key, [])
    if not org_lv3_options:
        dept_key = "Sales"
        org_lv3_options = lang_data["organizations"]["org_lv3"].get(dept_key, ["Default Department"])

    employee["org_lv3"] = random.choice(org_lv3_options)
    employee["org_lv4"] = random.choice(lang_data["organizations"]["org_lv4"])

    # Position and employment type
    employee["position"] = random.choices(
        lang_data["positions"]["choices"],
        weights=lang_data["positions"]["weights"],
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

    if is_contract:
        employee["position"] = lang_data["positions"]["choices"][0]  # Staff level
        base_salary = calculate_salary(config.salary_range, position_hierarchy, employee["position"])
        contract_salary = round(base_salary * 0.8, -3)
        employee["salary"] = max(contract_salary, config.salary_range[0])
    elif is_temporary:
        employee["position"] = lang_data["positions"]["choices"][0]  # Staff level
        employee["salary"] = None
    else:
        employee["salary"] = calculate_salary(
            config.salary_range, position_hierarchy, employee["position"]
        )

    # Engagement and performance
    if is_temporary:
        employee["engagement_score"] = None
        employee["performance"] = None
    else:
        engagement_score = np.random.normal(70, 15)
        engagement_score = max(0, min(100, round(engagement_score)))
        employee["engagement_score"] = engagement_score
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

    # Job grade
    if is_temporary:
        employee["job_grade"] = None
    else:
        employee["job_grade"] = position_to_grade.get(employee["position"], "Lv1")

    # Dates
    employee["hire_date"] = (
        current_date - timedelta(days=random.randint(0, 365 * 20))
    ).strftime("%Y-%m-%d")
    employee["resign_date"] = "2999-12-31"

    employee["is_married"] = random.choice([True, False])

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

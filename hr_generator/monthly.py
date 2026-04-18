"""Monthly simulation logic: snapshots, resignations, promotions, performance updates."""
import random
from datetime import datetime

from dateutil.relativedelta import relativedelta

from hr_generator.config import JOB_GRADE_SALARY_BANDS, RESIGNATION_REASONS
from hr_generator.employee import (
    adjust_organization_by_position,
    adjust_salary_by_performance,
    calculate_salary,
    get_performance_level,
    _build_position_to_grade,
)


def _get_resignation_reason(employee, config, lang_data):
    """Select an appropriate resignation reason (A6).

    Considers employee type, age, and engagement to pick a realistic reason.
    """
    language = config.language
    reasons = RESIGNATION_REASONS.get(language, RESIGNATION_REASONS["English"])
    emp_type_choices = lang_data["emp_types"]["choices"]

    # Contract expiry for contract employees
    if employee["emp_type"] == emp_type_choices[1]:
        # Higher chance of contract expiry
        if random.random() < 0.6:
            return reasons[3]  # "Contract Expiry" / "契約満了"

    # Retirement for older employees (age >= 58)
    birth_date = datetime.strptime(employee["birth_date"], "%Y-%m-%d")
    age = (datetime.now() - birth_date).days / 365.25
    if age >= 58:
        if random.random() < 0.5:
            return reasons[4]  # "Retirement" / "定年退職"

    # Voluntary reasons (weighted by engagement)
    voluntary_reasons = reasons[:3]  # Career change, personal, relocation
    return random.choice(voluntary_reasons)


def _calculate_resignation_probability(base_employee, base_date_dt, config):
    """Calculate adjusted resignation probability (A3 + A4).

    Short-tenure employees and low-engagement employees resign more often.
    """
    hire_date_dt = datetime.strptime(base_employee["hire_date"], "%Y-%m-%d")
    years_of_service = (base_date_dt - hire_date_dt).days / 365.25

    if years_of_service < 1:
        return 0.0  # Can't resign in first year

    # Base monthly probability from annual rate
    base_monthly_prob = 1 - (1 - config.resignation_rate) ** (1 / 12)

    # A3: Short tenure multiplier (1-3 years: 2x, 3-5 years: 1.5x, 5+ years: 1x)
    if years_of_service <= 3:
        tenure_multiplier = 2.0
    elif years_of_service <= 5:
        tenure_multiplier = 1.5
    else:
        tenure_multiplier = 1.0

    # A4: Low engagement multiplier
    engagement = base_employee.get("engagement_score")
    if engagement is not None:
        if engagement < 40:
            engagement_multiplier = 3.0
        elif engagement < 55:
            engagement_multiplier = 2.0
        elif engagement < 70:
            engagement_multiplier = 1.2
        else:
            engagement_multiplier = 0.7
    else:
        engagement_multiplier = 1.0

    raw_prob = base_monthly_prob * tenure_multiplier * engagement_multiplier
    # Cap monthly probability so annualized rate stays reasonable (~30% max)
    max_monthly_prob = 0.03
    return min(raw_prob, max_monthly_prob)


def generate_monthly_snapshot(base_employees, month_offset, base_date_str, config, lang_data):
    """Generate one month's worth of employee data.

    Returns:
        list of employee dicts for this month (rows to append to the dataset).
        base_employees is modified in place (resignations, promotions, salary updates).
    """
    rows = []
    base_date_dt = datetime.strptime(base_date_str, "%Y-%m-%d")
    position_to_grade = _build_position_to_grade(lang_data)
    emp_type_choices = lang_data["emp_types"]["choices"]

    for base_employee in base_employees:
        # Skip employees who already resigned before this month
        if base_employee["resign_date"] != "2999-12-31":
            resign_dt = datetime.strptime(base_employee["resign_date"], "%Y-%m-%d")
            if base_date_dt > resign_dt:
                continue

        employee = base_employee.copy()
        employee["base_date"] = base_date_str

        # --- Resignation logic (A3 + A4 + A6) ---
        # Only consider resignation for non-temporary, currently active employees
        if (
            base_employee["resign_date"] == "2999-12-31"
            and base_employee["emp_type"] != emp_type_choices[2]  # not temporary
        ):
            resign_prob = _calculate_resignation_probability(
                base_employee, base_date_dt, config
            )
            if resign_prob > 0 and random.random() < resign_prob:
                resign_date = (
                    base_date_dt + relativedelta(months=1, days=-1)
                ).strftime("%Y-%m-%d")
                base_employee["resign_date"] = resign_date
                employee["resign_date"] = resign_date
                # A6: Assign resignation reason
                reason = _get_resignation_reason(employee, config, lang_data)
                base_employee["resignation_reason"] = reason
                employee["resignation_reason"] = reason

        # --- Promotion logic (yearly, 5% chance) ---
        if (
            month_offset > 0
            and month_offset % 12 == 0
            and random.random() < 0.05
            and employee["emp_type"] != emp_type_choices[2]  # not temporary
        ):
            current_idx = lang_data["positions"]["choices"].index(employee["position"])
            if current_idx < len(lang_data["positions"]["choices"]) - 1:
                new_position = lang_data["positions"]["choices"][current_idx + 1]
                employee["position"] = new_position
                new_grade = position_to_grade[new_position]
                employee["job_grade"] = new_grade
                employee = adjust_organization_by_position(
                    employee, lang_data["positions"], new_position
                )
                # Update salary: keep performance raises, ensure within new grade band
                band_low, band_high = JOB_GRADE_SALARY_BANDS[new_grade]
                salary_span = config.salary_range[1] - config.salary_range[0]
                new_grade_min = config.salary_range[0] + salary_span * band_low
                new_grade_max = config.salary_range[0] + salary_span * band_high

                if employee["emp_type"] == emp_type_choices[1]:  # contract
                    promoted_salary = max(employee["salary"] or new_grade_min, new_grade_min)
                    promoted_salary = min(promoted_salary, new_grade_max)
                    employee["salary"] = max(round(promoted_salary * 0.8, -3), config.salary_range[0])
                elif employee["salary"] is not None:
                    # Preserve accumulated performance raises
                    promoted_salary = max(employee["salary"], new_grade_min)
                    promoted_salary = min(promoted_salary, new_grade_max)
                    employee["salary"] = round(promoted_salary, -3)

                # Persist to base
                base_employee["position"] = new_position
                base_employee["job_grade"] = new_grade
                base_employee["org_lv2"] = employee["org_lv2"]
                base_employee["org_lv3"] = employee["org_lv3"]
                base_employee["org_lv4"] = employee["org_lv4"]
                base_employee["salary"] = employee["salary"]

        # --- Performance and salary update (every 12 months) ---
        if month_offset > 0 and month_offset % 12 == 0:
            if employee["emp_type"] != emp_type_choices[2] and employee.get("engagement_score") is not None:
                hire_month = datetime.strptime(employee["hire_date"], "%Y-%m-%d").month
                current_month = base_date_dt.month
                if current_month == hire_month and base_date_str < employee["resign_date"]:
                    employee["performance"] = get_performance_level(employee["engagement_score"])
                    if employee["salary"] is not None:
                        adjusted = adjust_salary_by_performance(
                            employee["salary"], employee["performance"]
                        )
                        # Clamp salary to salary_range bounds
                        adjusted = max(adjusted, config.salary_range[0])
                        adjusted = min(adjusted, config.salary_range[1])
                        employee["salary"] = adjusted
                    base_employee["performance"] = employee["performance"]
                    base_employee["salary"] = employee["salary"]

        # --- Engagement score drift (30% chance each month) ---
        if (
            employee["emp_type"] != emp_type_choices[2]
            and employee.get("engagement_score") is not None
            and base_date_str < employee["resign_date"]
            and random.random() < 0.3
        ):
            new_score = round(
                min(max(employee["engagement_score"] * random.uniform(0.9, 1.1), 0), 100),
                0,
            )
            employee["engagement_score"] = new_score
            base_employee["engagement_score"] = new_score

        rows.append(employee)

    return rows

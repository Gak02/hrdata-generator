"""Monthly simulation logic: snapshots, resignations, promotions, performance updates."""
import random
from datetime import datetime

from dateutil.relativedelta import relativedelta

from hr_generator.employee import (
    adjust_organization_by_position,
    adjust_salary_by_performance,
    calculate_salary,
    get_performance_level,
    _build_position_hierarchy,
)


def generate_monthly_snapshot(base_employees, month_offset, base_date_str, config, lang_data):
    """Generate one month's worth of employee data.

    Returns:
        list of employee dicts for this month (rows to append to the dataset).
        base_employees is modified in place (resignations, promotions, salary updates).
    """
    rows = []
    base_date_dt = datetime.strptime(base_date_str, "%Y-%m-%d")
    position_hierarchy = _build_position_hierarchy(lang_data)
    emp_type_choices = lang_data["emp_types"]["choices"]

    for base_employee in base_employees:
        # Skip employees who already resigned before this month
        if base_employee["resign_date"] != "2999-12-31":
            resign_dt = datetime.strptime(base_employee["resign_date"], "%Y-%m-%d")
            if base_date_dt > resign_dt:
                continue

        employee = base_employee.copy()
        employee["base_date"] = base_date_str

        # --- Resignation logic ---
        # Only consider resignation for non-temporary, currently active employees
        if (
            base_employee["resign_date"] == "2999-12-31"
            and base_employee["emp_type"] != emp_type_choices[2]  # not temporary
        ):
            hire_date_dt = datetime.strptime(base_employee["hire_date"], "%Y-%m-%d")
            years_of_service = (base_date_dt - hire_date_dt).days / 365.25

            if years_of_service >= 1:
                monthly_resign_prob = 1 - (1 - config.resignation_rate) ** (1 / 12)
                if random.random() < monthly_resign_prob:
                    resign_date = (
                        base_date_dt + relativedelta(months=1, days=-1)
                    ).strftime("%Y-%m-%d")
                    base_employee["resign_date"] = resign_date
                    employee["resign_date"] = resign_date
                    # FIX P0: DO NOT skip this employee. They appear in their
                    # resignation month with resign_date set.

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
                employee = adjust_organization_by_position(
                    employee, lang_data["positions"], new_position
                )
                # Update salary for promoted position
                if employee["emp_type"] == emp_type_choices[1]:  # contract
                    base_salary = calculate_salary(
                        config.salary_range, position_hierarchy, new_position
                    )
                    contract_salary = round(base_salary * 0.8, -3)
                    employee["salary"] = max(contract_salary, config.salary_range[0])
                elif employee["salary"] is not None:
                    employee["salary"] = calculate_salary(
                        config.salary_range, position_hierarchy, new_position
                    )
                # Persist to base
                base_employee["position"] = new_position
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
                        employee["salary"] = adjust_salary_by_performance(
                            employee["salary"], employee["performance"]
                        )
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

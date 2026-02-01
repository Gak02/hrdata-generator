"""Top-level orchestrator for HR dataset generation."""
import random
from datetime import datetime

import numpy as np
import pandas as pd
from faker import Faker
from dateutil.relativedelta import relativedelta

from hr_generator.config import LANGUAGE_DATA
from hr_generator.employee import create_employee, validate_employee
from hr_generator.monthly import generate_monthly_snapshot
from hr_generator.models import GeneratorConfig


def _seed_all(seed):
    """Seed all random generators for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)


def generate_base_employees(config, lang_data, fake):
    """Generate exactly config.employee_count valid base employees.

    Unlike the old code, this has no attempt cap. It retries until the
    exact count is met. Since create_employee produces valid data for
    any reasonable config, this converges quickly.
    """
    employees = []
    employee_id = 1

    while len(employees) < config.employee_count:
        emp = create_employee(config, lang_data, fake, employee_id)
        is_valid, _ = validate_employee(
            emp,
            age_range=config.age_range,
            salary_range=config.salary_range,
            lang_data=lang_data,
        )
        if is_valid:
            employees.append(emp)
        employee_id += 1

    return employees


def generate_dataset(config):
    """Generate the full HR dataset as a DataFrame.

    Args:
        config: GeneratorConfig with all parameters.

    Returns:
        pd.DataFrame with one row per employee per month.
    """
    if config.random_seed is not None:
        _seed_all(config.random_seed)

    lang_data = LANGUAGE_DATA[config.language]
    locale = lang_data.get("faker_locale", "en_US")
    fake = Faker(locale)
    if config.random_seed is not None:
        fake.seed_instance(config.random_seed)

    # Generate base employees (exact count guaranteed)
    base_employees = generate_base_employees(config, lang_data, fake)

    # Generate monthly snapshots
    current_date = datetime.now()
    all_rows = []

    for month_offset in range(config.num_months):
        base_date = (
            current_date - relativedelta(months=(config.num_months - 1 - month_offset))
        ).replace(day=1).strftime("%Y-%m-%d")

        rows = generate_monthly_snapshot(
            base_employees, month_offset, base_date, config, lang_data
        )
        all_rows.extend(rows)

    if not all_rows:
        return pd.DataFrame()

    return pd.DataFrame(all_rows)

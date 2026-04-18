"""TDD tests for multi-month generation bugs.

BUG1: Salary drops below salary_range minimum after C performance adjustment.
BUG2: Resignation rate far exceeds user-specified annual rate due to A3+A4 multipliers.
BUG3: Salary can exceed salary_range maximum after S performance adjustment.
"""
import pytest
from datetime import datetime

from hr_generator.generator import generate_dataset
from hr_generator.models import GeneratorConfig
from hr_generator.monthly import _calculate_resignation_probability


class TestSalaryBoundsAfterPerformance:
    """BUG1 + BUG3: Salary must always stay within salary_range after updates."""

    def test_salary_never_below_minimum_24months(self):
        """Over 24 months, no salary should drop below salary_range minimum."""
        config = GeneratorConfig(
            language="Japanese", employee_count=300, num_months=24,
            age_range=(22, 60), salary_range=(3000000, 15000000), random_seed=99,
        )
        df = generate_dataset(config)
        salary_valid = df[df["salary"].notna()]
        below = salary_valid[salary_valid["salary"] < config.salary_range[0]]
        assert len(below) == 0, (
            f"{len(below)} rows have salary below {config.salary_range[0]}: "
            f"min={below['salary'].min()}"
        )

    def test_salary_never_above_maximum_24months(self):
        """Over 24 months, no salary should exceed salary_range maximum."""
        config = GeneratorConfig(
            language="English", employee_count=300, num_months=24,
            age_range=(25, 55), salary_range=(4000000, 10000000), random_seed=42,
        )
        df = generate_dataset(config)
        salary_valid = df[df["salary"].notna()]
        above = salary_valid[salary_valid["salary"] > config.salary_range[1]]
        assert len(above) == 0, (
            f"{len(above)} rows have salary above {config.salary_range[1]}: "
            f"max={above['salary'].max()}"
        )

    def test_salary_bounds_with_narrow_range(self):
        """Even with a narrow salary range, bounds must be respected."""
        config = GeneratorConfig(
            language="English", employee_count=200, num_months=24,
            age_range=(25, 55), salary_range=(5000000, 6000000), random_seed=42,
        )
        df = generate_dataset(config)
        salary_valid = df[df["salary"].notna()]
        below = salary_valid[salary_valid["salary"] < config.salary_range[0]]
        above = salary_valid[salary_valid["salary"] > config.salary_range[1]]
        assert len(below) == 0, f"Below min: {below['salary'].min()}"
        assert len(above) == 0, f"Above max: {above['salary'].max()}"


class TestResignationRateReasonable:
    """BUG2: Effective resignation rate should stay close to user-specified rate."""

    def test_resignation_rate_within_tolerance(self):
        """Over 24 months, total resignation rate should not exceed 3x the expected rate."""
        config = GeneratorConfig(
            language="English", employee_count=500, num_months=24,
            age_range=(22, 60), salary_range=(4000000, 10000000), random_seed=42,
        )
        df = generate_dataset(config)
        first_month = df["base_date"].min()
        first_count = len(
            df[(df["base_date"] == first_month) & (df["is_primary_position"] == True)]
        )
        resigned_unique = len(
            df[df["resign_date"] != "2999-12-31"].drop_duplicates("emp_id")
        )
        actual_rate = resigned_unique / first_count

        # Expected 2-year rate: 1 - (1 - 0.10)^2 = 0.19
        # Allow up to 1.5x tolerance → 0.285
        expected_2yr = 1 - (1 - config.resignation_rate) ** 2
        max_tolerance = expected_2yr * 1.5
        assert actual_rate <= max_tolerance, (
            f"Resignation rate {actual_rate:.1%} exceeds tolerance "
            f"{max_tolerance:.1%} (expected ~{expected_2yr:.1%})"
        )

    def test_resignation_probability_capped(self):
        """Monthly resignation probability should have an upper cap."""
        # Worst case: short tenure + very low engagement
        base_employee = {
            "hire_date": "2023-01-01",
            "engagement_score": 20,
            "resign_date": "2999-12-31",
        }

        class FakeConfig:
            resignation_rate = 0.10

        base_date = datetime(2024, 7, 1)
        prob = _calculate_resignation_probability(base_employee, base_date, FakeConfig())
        # Monthly probability should not exceed ~3% (annualized ~30%)
        assert prob <= 0.03, (
            f"Monthly resignation probability {prob:.4f} too high "
            f"(annualized {1-(1-prob)**12:.1%})"
        )


class TestMultiMonthDataConsistency:
    """Ensure all fields are consistent across months."""

    def test_no_orphaned_resignation_reasons(self):
        """Active employees must not have a resignation_reason."""
        config = GeneratorConfig(
            language="English", employee_count=200, num_months=12,
            age_range=(25, 55), salary_range=(4000000, 10000000), random_seed=42,
        )
        df = generate_dataset(config)
        active = df[df["resign_date"] == "2999-12-31"]
        with_reason = active[active["resignation_reason"].notna()]
        assert len(with_reason) == 0, f"{len(with_reason)} active employees have resignation_reason"

    def test_contract_end_date_consistent_across_months(self):
        """contract_end_date should not change across months for the same employee."""
        config = GeneratorConfig(
            language="English", employee_count=200, num_months=12,
            age_range=(25, 55), salary_range=(4000000, 10000000), random_seed=42,
        )
        df = generate_dataset(config)
        contracts = df[df["emp_type"] == "Contract"]
        for emp_id in contracts["emp_id"].unique():
            emp_rows = contracts[contracts["emp_id"] == emp_id]
            end_dates = emp_rows["contract_end_date"].unique()
            assert len(end_dates) == 1, (
                f"{emp_id} has inconsistent contract_end_date: {end_dates}"
            )

    def test_first_month_has_exact_employee_count(self):
        """First month should always have exactly the requested employee count."""
        for count in [100, 200, 500]:
            config = GeneratorConfig(
                language="English", employee_count=count, num_months=6,
                age_range=(25, 55), salary_range=(4000000, 10000000), random_seed=42,
            )
            df = generate_dataset(config)
            first_month = df["base_date"].min()
            first_primary = df[
                (df["base_date"] == first_month) & (df["is_primary_position"] == True)
            ]
            assert len(first_primary) == count, (
                f"Expected {count}, got {len(first_primary)}"
            )

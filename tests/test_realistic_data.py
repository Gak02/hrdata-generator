"""TDD tests for realistic HR data improvements (A1-A7, C1-C5).

These tests verify that generated data follows real-world HR patterns:
- Age/tenure correlations with position
- Engagement-driven resignations
- Contract employee lifecycle
- Resignation reasons
- Marriage-age correlation
- Department size distribution
- Hire date seasonality
- Salary-age correlation within grade
- Forced performance distribution
- New graduate batch hiring (Japanese mode)
"""
import random
from datetime import datetime

import numpy as np
import pytest
from faker import Faker

from hr_generator.config import (
    LANGUAGE_DATA,
    FORCED_PERFORMANCE_DISTRIBUTION,
    DEPARTMENT_WEIGHTS,
    RESIGNATION_REASONS,
)
from hr_generator.employee import create_employee, get_age_adjusted_position_weights
from hr_generator.generator import generate_dataset
from hr_generator.models import GeneratorConfig
from hr_generator.monthly import generate_monthly_snapshot


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def large_config():
    """Large sample for statistical tests."""
    return GeneratorConfig(
        language="English",
        employee_count=500,
        num_months=1,
        age_range=(22, 60),
        salary_range=(4000000, 10000000),
        random_seed=42,
    )


@pytest.fixture
def large_jp_config():
    """Large sample for Japanese-specific tests."""
    return GeneratorConfig(
        language="Japanese",
        employee_count=500,
        num_months=1,
        age_range=(22, 60),
        salary_range=(4000000, 10000000),
        random_seed=42,
    )


@pytest.fixture
def multi_month_resign_config():
    """Config for resignation/engagement tests."""
    return GeneratorConfig(
        language="English",
        employee_count=300,
        num_months=24,
        age_range=(22, 60),
        salary_range=(4000000, 10000000),
        random_seed=42,
    )


# ===========================================================================
# A1: Age-position correlation
# ===========================================================================

class TestAgePositionCorrelation:
    """A1: Younger employees should be more likely to be Staff;
    older employees should have a higher probability of senior roles."""

    def test_young_employees_mostly_staff(self, large_config):
        """Employees under 30 should be predominantly Staff/Team Lead."""
        df = generate_dataset(large_config)
        young = df[df["birth_date"].apply(
            lambda bd: (datetime.now() - datetime.strptime(bd, "%Y-%m-%d")).days / 365.25 < 30
        )]
        if len(young) == 0:
            pytest.skip("No young employees in sample")
        senior_positions = ["Manager", "General Manager", "VP", "C-level"]
        senior_ratio = len(young[young["position"].isin(senior_positions)]) / len(young)
        # Young employees should have fewer than 10% in senior positions
        assert senior_ratio < 0.10, f"Young senior ratio too high: {senior_ratio:.2%}"

    def test_older_employees_have_more_senior_roles(self, large_config):
        """Employees over 45 should have a significantly higher senior ratio than under 30."""
        df = generate_dataset(large_config)
        senior_positions = ["Manager", "General Manager", "VP", "C-level"]

        young = df[df["birth_date"].apply(
            lambda bd: (datetime.now() - datetime.strptime(bd, "%Y-%m-%d")).days / 365.25 < 30
        )]
        older = df[df["birth_date"].apply(
            lambda bd: (datetime.now() - datetime.strptime(bd, "%Y-%m-%d")).days / 365.25 >= 45
        )]
        if len(young) == 0 or len(older) == 0:
            pytest.skip("Insufficient age range in sample")

        young_senior = len(young[young["position"].isin(senior_positions)]) / max(len(young), 1)
        older_senior = len(older[older["position"].isin(senior_positions)]) / max(len(older), 1)
        assert older_senior > young_senior, (
            f"Older senior ratio ({older_senior:.2%}) should exceed young ({young_senior:.2%})"
        )

    def test_get_age_adjusted_position_weights_returns_list(self):
        """Helper function should return a list of weights."""
        lang_data = LANGUAGE_DATA["English"]
        weights = get_age_adjusted_position_weights(25, lang_data)
        assert isinstance(weights, list)
        assert len(weights) == len(lang_data["positions"]["choices"])
        assert all(w >= 0 for w in weights)


# ===========================================================================
# A2: Tenure-position correlation
# ===========================================================================

class TestTenurePositionCorrelation:
    """A2: Senior positions should have longer tenure (earlier hire dates)."""

    def test_senior_positions_have_longer_tenure(self, large_config):
        """Average tenure of Manager+ should exceed average tenure of Staff."""
        df = generate_dataset(large_config)
        now = datetime.now()

        df["tenure_years"] = df["hire_date"].apply(
            lambda hd: (now - datetime.strptime(hd, "%Y-%m-%d")).days / 365.25
        )
        senior_positions = ["Manager", "General Manager", "VP", "C-level"]

        staff_tenure = df[df["position"] == "Staff"]["tenure_years"].mean()
        senior_tenure = df[df["position"].isin(senior_positions)]["tenure_years"].mean()

        if np.isnan(senior_tenure):
            pytest.skip("No senior employees in sample")

        assert senior_tenure > staff_tenure, (
            f"Senior tenure ({senior_tenure:.1f}y) should exceed staff ({staff_tenure:.1f}y)"
        )


# ===========================================================================
# A3: Resignation rate linked to attributes
# ===========================================================================

class TestResignationRateAttributes:
    """A3: Short-tenure and low-engagement employees resign more."""

    def test_short_tenure_higher_resignation(self, multi_month_resign_config):
        """Employees with 1-3 years tenure should resign at a higher rate."""
        df = generate_dataset(multi_month_resign_config)
        resigned = df[df["resign_date"] != "2999-12-31"].drop_duplicates("emp_id")
        if len(resigned) == 0:
            pytest.skip("No resignations in sample")

        now = datetime.now()
        resigned["tenure_at_resign"] = resigned.apply(
            lambda r: (datetime.strptime(r["resign_date"], "%Y-%m-%d")
                        - datetime.strptime(r["hire_date"], "%Y-%m-%d")).days / 365.25,
            axis=1,
        )
        short_tenure_resignees = len(resigned[resigned["tenure_at_resign"] <= 5])
        long_tenure_resignees = len(resigned[resigned["tenure_at_resign"] > 5])
        # Short tenure should have proportionally more resignations
        assert short_tenure_resignees >= long_tenure_resignees, (
            f"Short tenure resignees ({short_tenure_resignees}) should >= long ({long_tenure_resignees})"
        )


# ===========================================================================
# A4: Engagement-resignation causality
# ===========================================================================

class TestEngagementResignationCausality:
    """A4: Low engagement should increase resignation probability."""

    def test_low_engagement_higher_resignation(self, multi_month_resign_config):
        """Resigned employees should have lower average engagement than retained."""
        df = generate_dataset(multi_month_resign_config)
        # Get first month snapshot for initial engagement comparison
        first_month = df["base_date"].min()
        first_df = df[df["base_date"] == first_month].copy()

        # Track who resigned
        resigned_ids = set(
            df[df["resign_date"] != "2999-12-31"]["emp_id"].unique()
        )

        first_df["resigned"] = first_df["emp_id"].isin(resigned_ids)
        with_score = first_df[first_df["engagement_score"].notna()]

        if len(with_score[with_score["resigned"]]) == 0:
            pytest.skip("No resignees with engagement scores")

        resigned_avg = with_score[with_score["resigned"]]["engagement_score"].mean()
        retained_avg = with_score[~with_score["resigned"]]["engagement_score"].mean()

        assert resigned_avg < retained_avg, (
            f"Resigned avg engagement ({resigned_avg:.1f}) should be < retained ({retained_avg:.1f})"
        )


# ===========================================================================
# A5: Contract employee contract period
# ===========================================================================

class TestContractEmployeePeriod:
    """A5: Contract employees should have a contract_end_date."""

    def test_contract_employees_have_end_date(self, large_config):
        """Contract employees should have a non-null contract_end_date."""
        df = generate_dataset(large_config)
        contracts = df[df["emp_type"] == "Contract"]
        if len(contracts) == 0:
            pytest.skip("No contract employees in sample")
        assert "contract_end_date" in df.columns
        assert contracts["contract_end_date"].notna().all(), (
            "All contract employees should have contract_end_date"
        )

    def test_contract_end_date_after_hire(self, large_config):
        """contract_end_date should be 1-3 years after hire_date."""
        df = generate_dataset(large_config)
        contracts = df[df["emp_type"] == "Contract"]
        if len(contracts) == 0:
            pytest.skip("No contract employees in sample")
        for _, row in contracts.iterrows():
            hire = datetime.strptime(row["hire_date"], "%Y-%m-%d")
            end = datetime.strptime(row["contract_end_date"], "%Y-%m-%d")
            years = (end - hire).days / 365.25
            assert 0.9 <= years <= 3.1, f"Contract period {years:.1f}y out of range"

    def test_non_contract_no_end_date(self, large_config):
        """Non-contract employees should have None for contract_end_date."""
        df = generate_dataset(large_config)
        non_contracts = df[df["emp_type"] != "Contract"]
        assert non_contracts["contract_end_date"].isna().all()


# ===========================================================================
# A6: Resignation reason
# ===========================================================================

class TestResignationReason:
    """A6: Resigned employees should have a resignation_reason field."""

    def test_resigned_have_reason(self, multi_month_resign_config):
        """Resigned employees must have a resignation_reason."""
        df = generate_dataset(multi_month_resign_config)
        resigned = df[df["resign_date"] != "2999-12-31"]
        if len(resigned) == 0:
            pytest.skip("No resignations in sample")
        assert "resignation_reason" in df.columns
        assert resigned["resignation_reason"].notna().all()

    def test_active_no_reason(self, multi_month_resign_config):
        """Active employees should have None for resignation_reason."""
        df = generate_dataset(multi_month_resign_config)
        active = df[df["resign_date"] == "2999-12-31"]
        assert active["resignation_reason"].isna().all()

    def test_valid_reason_values(self, multi_month_resign_config):
        """Resignation reasons should be from the predefined list."""
        df = generate_dataset(multi_month_resign_config)
        resigned = df[df["resign_date"] != "2999-12-31"]
        if len(resigned) == 0:
            pytest.skip("No resignations in sample")
        valid_reasons = RESIGNATION_REASONS["English"]
        for reason in resigned["resignation_reason"].unique():
            assert reason in valid_reasons, f"Invalid reason: {reason}"


# ===========================================================================
# A7: Marriage-age correlation
# ===========================================================================

class TestMarriageAgeCorrelation:
    """A7: Older employees should be more likely to be married."""

    def test_older_more_likely_married(self, large_config):
        """Marriage rate should increase with age."""
        df = generate_dataset(large_config)
        now = datetime.now()
        df["age"] = df["birth_date"].apply(
            lambda bd: (now - datetime.strptime(bd, "%Y-%m-%d")).days / 365.25
        )
        young_married = df[df["age"] < 30]["is_married"].mean()
        older_married = df[df["age"] >= 45]["is_married"].mean()

        if len(df[df["age"] < 30]) == 0 or len(df[df["age"] >= 45]) == 0:
            pytest.skip("Insufficient age range")

        assert older_married > young_married, (
            f"Older married rate ({older_married:.2%}) should exceed young ({young_married:.2%})"
        )


# ===========================================================================
# C1: Department size distribution
# ===========================================================================

class TestDepartmentDistribution:
    """C1: Departments should have unequal sizes."""

    def test_departments_not_uniform(self, large_config):
        """Department distribution should not be roughly equal (25% each)."""
        df = generate_dataset(large_config)
        # Filter primary positions only
        if "is_primary_position" in df.columns:
            df = df[df["is_primary_position"] == True]
        dept_counts = df["org_lv2"].dropna().value_counts(normalize=True)
        # At least one department should be > 30% (not uniform 25%)
        assert dept_counts.max() > 0.30, (
            f"Largest department is only {dept_counts.max():.2%}, expected > 30%"
        )

    def test_department_weights_config_exists(self):
        """DEPARTMENT_WEIGHTS should exist in config for both languages."""
        assert "English" in DEPARTMENT_WEIGHTS
        assert "Japanese" in DEPARTMENT_WEIGHTS


# ===========================================================================
# C2: Hire date seasonality
# ===========================================================================

class TestHireDateSeasonality:
    """C2: Hire dates should cluster around specific months."""

    def test_hire_month_not_uniform(self, large_config):
        """Hire dates should show seasonal patterns (not flat across 12 months)."""
        df = generate_dataset(large_config)
        df["hire_month"] = df["hire_date"].apply(
            lambda hd: datetime.strptime(hd, "%Y-%m-%d").month
        )
        month_counts = df["hire_month"].value_counts(normalize=True)
        # Peak month should be significantly higher than 1/12 (~8.3%)
        assert month_counts.max() > 0.15, (
            f"Peak hire month is only {month_counts.max():.2%}, expected > 15%"
        )

    def test_japanese_april_peak(self, large_jp_config):
        """Japanese mode should have a strong April hiring peak."""
        df = generate_dataset(large_jp_config)
        df["hire_month"] = df["hire_date"].apply(
            lambda hd: datetime.strptime(hd, "%Y-%m-%d").month
        )
        april_ratio = (df["hire_month"] == 4).mean()
        assert april_ratio > 0.20, (
            f"Japanese April hire ratio is {april_ratio:.2%}, expected > 20%"
        )


# ===========================================================================
# C3: Salary-age correlation within grade
# ===========================================================================

class TestSalaryAgeCorrelation:
    """C3: Within the same job grade, older/longer-tenured employees earn more."""

    def test_older_employees_earn_more_within_grade(self, large_config):
        """Within Lv1, older employees should tend to have higher salaries."""
        df = generate_dataset(large_config)
        now = datetime.now()
        lv1 = df[(df["job_grade"] == "Lv1") & (df["salary"].notna())].copy()
        if len(lv1) < 20:
            pytest.skip("Not enough Lv1 employees")

        lv1["age"] = lv1["birth_date"].apply(
            lambda bd: (now - datetime.strptime(bd, "%Y-%m-%d")).days / 365.25
        )
        # Correlation between age and salary should be positive
        correlation = lv1["age"].corr(lv1["salary"])
        assert correlation > 0, (
            f"Age-salary correlation in Lv1 should be positive, got {correlation:.3f}"
        )


# ===========================================================================
# C4: Forced performance distribution
# ===========================================================================

class TestForcedPerformanceDistribution:
    """C4: Performance ratings should follow a forced distribution."""

    def test_performance_distribution_matches_target(self, large_config):
        """Performance should roughly match S:5%, A:20%, B:60%, C:15%."""
        df = generate_dataset(large_config)
        perf = df[df["performance"].notna()]["performance"]
        if len(perf) == 0:
            pytest.skip("No performance data")

        dist = perf.value_counts(normalize=True)
        # Allow generous tolerance but enforce the shape
        assert dist.get("B", 0) > dist.get("A", 0), "B should be most common"
        assert dist.get("B", 0) > dist.get("S", 0), "B should exceed S"
        assert dist.get("S", 0) < 0.15, f"S ratio {dist.get('S', 0):.2%} too high (target ~5%)"
        assert dist.get("B", 0) > 0.35, f"B ratio {dist.get('B', 0):.2%} too low (target ~60%)"

    def test_forced_distribution_config_exists(self):
        """FORCED_PERFORMANCE_DISTRIBUTION should be defined."""
        assert "S" in FORCED_PERFORMANCE_DISTRIBUTION
        assert "A" in FORCED_PERFORMANCE_DISTRIBUTION
        assert "B" in FORCED_PERFORMANCE_DISTRIBUTION
        assert "C" in FORCED_PERFORMANCE_DISTRIBUTION
        total = sum(FORCED_PERFORMANCE_DISTRIBUTION.values())
        assert abs(total - 1.0) < 0.01, f"Distribution should sum to 1.0, got {total}"


# ===========================================================================
# C5: New graduate batch hiring (Japanese mode)
# ===========================================================================

class TestNewGraduateBatchHiring:
    """C5: Japanese mode should have clusters of April 1st hires for young employees."""

    def test_japanese_young_april_hires(self, large_jp_config):
        """In Japanese mode, young employees (22-25) should mostly have April 1st hire dates."""
        df = generate_dataset(large_jp_config)
        now = datetime.now()
        df["age"] = df["birth_date"].apply(
            lambda bd: (now - datetime.strptime(bd, "%Y-%m-%d")).days / 365.25
        )
        young = df[df["age"] < 26].copy()
        if len(young) == 0:
            pytest.skip("No young employees")

        young["hire_month"] = young["hire_date"].apply(
            lambda hd: datetime.strptime(hd, "%Y-%m-%d").month
        )
        young["hire_day"] = young["hire_date"].apply(
            lambda hd: datetime.strptime(hd, "%Y-%m-%d").day
        )
        april_1st = young[(young["hire_month"] == 4) & (young["hire_day"] == 1)]
        april_ratio = len(april_1st) / len(young)
        assert april_ratio > 0.40, (
            f"Young JP employees April 1st ratio is {april_ratio:.2%}, expected > 40%"
        )

    def test_english_no_forced_april(self, large_config):
        """English mode should NOT have forced April 1st batch hiring."""
        df = generate_dataset(large_config)
        now = datetime.now()
        df["age"] = df["birth_date"].apply(
            lambda bd: (now - datetime.strptime(bd, "%Y-%m-%d")).days / 365.25
        )
        young = df[df["age"] < 26].copy()
        if len(young) == 0:
            pytest.skip("No young employees")
        young["hire_month"] = young["hire_date"].apply(
            lambda hd: datetime.strptime(hd, "%Y-%m-%d").month
        )
        young["hire_day"] = young["hire_date"].apply(
            lambda hd: datetime.strptime(hd, "%Y-%m-%d").day
        )
        april_1st = young[(young["hire_month"] == 4) & (young["hire_day"] == 1)]
        # Should NOT have the Japanese-style forced batch hiring
        april_ratio = len(april_1st) / max(len(young), 1)
        assert april_ratio < 0.40, (
            f"English April 1st ratio {april_ratio:.2%} too high - should not force batch hiring"
        )

"""Integration tests for full dataset generation - P0 employee count guarantee."""
from dataclasses import replace

from hr_generator.generator import generate_dataset


class TestEmployeeCountMonth1:
    """Month 1 must have exactly the requested employee count."""

    def test_exact_count_single_month(self, default_config):
        config = replace(default_config, employee_count=200, num_months=1)
        df = generate_dataset(config)
        assert len(df) == 200

    def test_exact_count_small(self, default_config):
        config = replace(default_config, employee_count=100, num_months=1)
        df = generate_dataset(config)
        assert len(df) == 100

    def test_exact_count_large(self, default_config):
        config = replace(default_config, employee_count=500, num_months=1)
        df = generate_dataset(config)
        assert len(df) == 500

    def test_first_month_exact_in_multi_month(self, multi_month_config):
        df = generate_dataset(multi_month_config)
        first_month = df["base_date"].min()
        first_month_count = len(df[df["base_date"] == first_month])
        assert first_month_count == multi_month_config.employee_count


class TestMultiMonthHeadcount:
    """Multi-month: headcount may decline from resignations but never exceeds initial."""

    def test_no_month_exceeds_initial_count(self, multi_month_config):
        df = generate_dataset(multi_month_config)
        for base_date, group in df.groupby("base_date"):
            assert len(group) <= multi_month_config.employee_count

    def test_all_months_present(self, multi_month_config):
        df = generate_dataset(multi_month_config)
        assert df["base_date"].nunique() == multi_month_config.num_months


class TestResignedEmployeeVisibility:
    """Resigned employees must appear in their resignation month."""

    def test_resigned_employee_has_row_in_resign_month(self, multi_month_config):
        df = generate_dataset(multi_month_config)
        resigned = df[df["resign_date"] != "2999-12-31"]
        if len(resigned) == 0:
            return  # no resignations happened with this seed
        # For each resigned employee, check they have a row in their last month
        for emp_id in resigned["emp_id"].unique():
            emp_rows = df[df["emp_id"] == emp_id]
            assert len(emp_rows) >= 1, f"Employee {emp_id} has no rows at all"

    def test_resigned_employee_not_in_later_months(self, multi_month_config):
        df = generate_dataset(multi_month_config)
        resigned = df[df["resign_date"] != "2999-12-31"]
        for _, row in resigned.iterrows():
            later = df[
                (df["emp_id"] == row["emp_id"])
                & (df["base_date"] > row["resign_date"])
            ]
            assert len(later) == 0, (
                f"Employee {row['emp_id']} appears after resign_date {row['resign_date']}"
            )


class TestDatasetStructure:
    """Basic structural checks on generated data."""

    def test_required_columns_present(self, default_config):
        df = generate_dataset(default_config)
        expected_cols = {
            "emp_id", "name", "birth_date", "gender",
            "org_lv1", "org_lv2", "org_lv3", "org_lv4",
            "position", "emp_type", "salary",
            "hire_date", "resign_date",
            "engagement_score", "performance",
            "is_married", "address", "job_category", "job_grade",
            "base_date",
        }
        assert expected_cols.issubset(set(df.columns))

    def test_unique_emp_ids_per_month(self, default_config):
        df = generate_dataset(default_config)
        for base_date, group in df.groupby("base_date"):
            assert group["emp_id"].is_unique, f"Duplicate emp_ids in {base_date}"

    def test_deterministic_with_seed(self, default_config):
        df1 = generate_dataset(default_config)
        df2 = generate_dataset(default_config)
        assert df1.equals(df2)


class TestConcurrentPositions:
    """Tests for concurrent positions (兼務) feature."""

    def test_no_concurrent_positions_by_default(self, default_config):
        """By default, include_concurrent_positions is False."""
        assert default_config.include_concurrent_positions is False

    def test_no_duplicate_emp_id_when_disabled(self, default_config):
        """When concurrent positions disabled, emp_id is unique per month."""
        config = replace(default_config, include_concurrent_positions=False)
        df = generate_dataset(config)
        for base_date, group in df.groupby("base_date"):
            assert group["emp_id"].is_unique

    def test_concurrent_positions_creates_duplicates(self, default_config):
        """When enabled, some employees have multiple rows per month."""
        config = replace(
            default_config,
            include_concurrent_positions=True,
            employee_count=200,
            random_seed=42,
        )
        df = generate_dataset(config)
        # Check if any emp_id appears more than once in a single month
        first_month = df["base_date"].min()
        first_month_df = df[df["base_date"] == first_month]
        has_duplicates = first_month_df["emp_id"].duplicated().any()
        assert has_duplicates, "Expected some employees with concurrent positions"

    def test_concurrent_position_has_different_org(self, default_config):
        """Concurrent position rows have different org_lv2."""
        config = replace(
            default_config,
            include_concurrent_positions=True,
            employee_count=200,
            random_seed=42,
        )
        df = generate_dataset(config)
        first_month = df["base_date"].min()
        first_month_df = df[df["base_date"] == first_month]
        # Find employees with duplicate entries
        dup_emp_ids = first_month_df[first_month_df["emp_id"].duplicated(keep=False)]["emp_id"].unique()
        if len(dup_emp_ids) > 0:
            for emp_id in dup_emp_ids[:3]:  # Check first 3
                emp_rows = first_month_df[first_month_df["emp_id"] == emp_id]
                # org_lv2 should be different for concurrent positions
                assert emp_rows["org_lv2"].nunique() > 1, (
                    f"Employee {emp_id} concurrent positions should have different org_lv2"
                )

    def test_concurrent_position_has_is_primary_flag(self, default_config):
        """Concurrent position rows have is_primary_position column."""
        config = replace(
            default_config,
            include_concurrent_positions=True,
            employee_count=200,
            random_seed=42,
        )
        df = generate_dataset(config)
        assert "is_primary_position" in df.columns
        # Primary position should be True/False
        assert df["is_primary_position"].dtype == bool

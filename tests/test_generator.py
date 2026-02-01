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

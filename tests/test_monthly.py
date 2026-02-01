"""Tests for monthly simulation logic - P0 and P2."""
from dataclasses import replace

from hr_generator.generator import generate_dataset


class TestMonthlyResignation:
    """Resignation logic must be correct."""

    def test_resign_date_after_hire_date(self, multi_month_config):
        df = generate_dataset(multi_month_config)
        resigned = df[df["resign_date"] != "2999-12-31"]
        for _, row in resigned.iterrows():
            assert row["resign_date"] >= row["hire_date"], (
                f"Employee {row['emp_id']}: resign_date {row['resign_date']} "
                f"before hire_date {row['hire_date']}"
            )

    def test_headcount_monotonically_nonincreasing(self, multi_month_config):
        """Headcount should never increase (no backfill per user preference)."""
        df = generate_dataset(multi_month_config)
        monthly_counts = df.groupby("base_date").size().sort_index()
        counts = monthly_counts.values.tolist()
        for i in range(1, len(counts)):
            assert counts[i] <= counts[i - 1], (
                f"Headcount increased from {counts[i-1]} to {counts[i]}"
            )


class TestMonthlyPerformanceUpdate:
    """Performance and salary update every 12 months."""

    def test_engagement_score_bounded(self, multi_month_config):
        df = generate_dataset(multi_month_config)
        scores = df["engagement_score"].dropna()
        assert (scores >= 0).all()
        assert (scores <= 100).all()


class TestMonthlyPromotions:
    """Promotions should not break data integrity."""

    def test_promoted_employee_has_valid_org(self, multi_month_config):
        df = generate_dataset(multi_month_config)
        # Executives should have null org_lv2/lv3/lv4
        lang_data_positions = {"VP", "C-level"}
        executives = df[df["position"].isin(lang_data_positions)]
        if len(executives) > 0:
            assert executives["org_lv2"].isna().all() | (executives["org_lv2"] == "").all() | (executives["org_lv2"].isnull()).all()

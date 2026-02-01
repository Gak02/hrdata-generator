"""Tests for performance level mapping - P1 deduplication."""
from hr_generator.employee import get_performance_level


class TestGetPerformanceLevel:
    """Single canonical function for engagement -> performance mapping."""

    def test_s_level_at_90(self):
        assert get_performance_level(90) == "S"

    def test_s_level_at_100(self):
        assert get_performance_level(100) == "S"

    def test_s_level_at_95(self):
        assert get_performance_level(95) == "S"

    def test_a_level_at_89(self):
        assert get_performance_level(89) == "A"

    def test_a_level_at_75(self):
        assert get_performance_level(75) == "A"

    def test_b_level_at_74(self):
        assert get_performance_level(74) == "B"

    def test_b_level_at_50(self):
        assert get_performance_level(50) == "B"

    def test_c_level_at_49(self):
        assert get_performance_level(49) == "C"

    def test_c_level_at_0(self):
        assert get_performance_level(0) == "C"


class TestNoDuplicatePerformanceFunction:
    """update_performance_based_on_engagement should not exist."""

    def test_no_duplicate_function(self):
        from hr_generator import employee
        assert not hasattr(employee, "update_performance_based_on_engagement")

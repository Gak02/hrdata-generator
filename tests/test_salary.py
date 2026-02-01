"""Tests for salary calculation and label - P1 and P2."""
from hr_generator.employee import calculate_salary, adjust_salary_by_performance
from hr_generator.config import TRANSLATIONS


class TestCalculateSalary:
    def test_within_range(self):
        salary_range = (4000000, 10000000)
        position_hierarchy = {"Staff": 1, "Manager": 2, "VP": 3}
        for position in position_hierarchy:
            salary = calculate_salary(salary_range, position_hierarchy, position)
            assert salary_range[0] <= salary <= salary_range[1]

    def test_higher_position_higher_salary(self):
        salary_range = (4000000, 10000000)
        position_hierarchy = {"Staff": 1, "Manager": 2, "VP": 3}
        staff_salary = calculate_salary(salary_range, position_hierarchy, "Staff")
        mgr_salary = calculate_salary(salary_range, position_hierarchy, "Manager")
        vp_salary = calculate_salary(salary_range, position_hierarchy, "VP")
        assert staff_salary <= mgr_salary <= vp_salary

    def test_rounded_to_thousands(self):
        salary_range = (4000000, 10000000)
        position_hierarchy = {"Staff": 1, "Manager": 2}
        salary = calculate_salary(salary_range, position_hierarchy, "Staff")
        assert salary % 1000 == 0


class TestAdjustSalaryByPerformance:
    def test_s_performance_increases(self):
        result = adjust_salary_by_performance(5000000, "S")
        assert result > 5000000

    def test_c_performance_decreases(self):
        result = adjust_salary_by_performance(5000000, "C")
        assert result < 5000000

    def test_rounded_to_thousands(self):
        result = adjust_salary_by_performance(5000000, "A")
        assert result % 1000 == 0


class TestSalaryLabel:
    """English locale salary label should not hardcode (JPY)."""

    def test_english_salary_label_no_jpy(self):
        label = TRANSLATIONS["English"]["salary_range"]
        assert "(JPY)" not in label

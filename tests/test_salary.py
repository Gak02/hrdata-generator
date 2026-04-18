"""Tests for salary calculation and label - P1 and P2."""
import random

from hr_generator.employee import calculate_salary, adjust_salary_by_performance
from hr_generator.config import TRANSLATIONS, JOB_GRADE_SALARY_BANDS


class TestCalculateSalary:
    def test_within_range(self):
        """Each grade's salary must fall within the overall salary_range."""
        salary_range = (4000000, 10000000)
        for grade in JOB_GRADE_SALARY_BANDS:
            salary = calculate_salary(salary_range, grade)
            assert salary_range[0] <= salary <= salary_range[1]

    def test_higher_grade_has_higher_band_midpoint(self):
        """Higher job grades should have higher band midpoints."""
        salary_range = (4000000, 10000000)
        grades = ["Lv1", "Lv2", "Lv3", "Lv4", "Lv5", "Lv6"]
        midpoints = []
        for grade in grades:
            band_low, band_high = JOB_GRADE_SALARY_BANDS[grade]
            midpoint = (band_low + band_high) / 2
            midpoints.append(midpoint)
        for i in range(len(midpoints) - 1):
            assert midpoints[i] < midpoints[i + 1]

    def test_rounded_to_thousands(self):
        salary_range = (4000000, 10000000)
        salary = calculate_salary(salary_range, "Lv1")
        assert salary % 1000 == 0

    def test_salary_varies_within_grade(self):
        """Same grade should produce different salaries (random variation)."""
        salary_range = (4000000, 10000000)
        random.seed(None)
        salaries = {calculate_salary(salary_range, "Lv3") for _ in range(50)}
        assert len(salaries) > 1, "Salary should vary within the same grade"


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
